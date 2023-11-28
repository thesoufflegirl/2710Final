from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import date

bp = Blueprint('store', __name__)


@bp.route('/', methods=['GET','POST'])
def index():
    print('I went back to the right place')
    db = get_db()
    session.get('genreList', [])
    genre = db.execute('SELECT DISTINCT genreClassification FROM Products').fetchall()
    genreList = []
    for a in genre:
        genreList.append(a['genreClassification'])
    genreList.append('select')
    session['genreList'] = genreList
    products = db.execute(
        'SELECT productID, title,price FROM Products'
    ).fetchall() 
    return render_template('store/index.html', products=products, genreList = genreList)

@bp.route('/cart', methods=('GET', 'POST'))
def cart():
    total = 0
    db = get_db()
    products = db.execute(
        'SELECT productID, title,price FROM Products'
    ).fetchall() 
    cart = session.get('cart', {'1':0, '2':0, '3':0,'4':0,'5':0,'6':0,'7':0,'8':0,'9':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0})
    print(cart)
    for item in cart:
        for product in products:
            id = str(product['productID'])
            price = db.execute('SELECT price FROM Products WHERE productID = ?',(id,)).fetchone()['price']
            if str(product['productID']) == item:
               total +=  cart[item]*price

        
    return render_template('store/cart.html', products=products,cart = cart,total = total)

@login_required


@bp.route("/add", methods=['GET','POST'])
def add():
    cart = session.get('cart', {'1':0, '2':0, '3':0,'4':0,'5':0,'6':0,'7':0,'8':0,'9':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0})
    code = request.form['code']
    quantity = int(request.form['quantity'])
    cart[code] = cart[code]+quantity
    session['cart'] = cart
    print(cart)
    return redirect(url_for('index'))

@bp.route("/edit", methods=['GET','POST'])
def edit():
    cart = session.get('cart')
    code = request.form['code']
    quantity = int(request.form['quantity'])
    cart[code] = quantity
    session['cart'] = cart
    print(cart)
    return redirect(url_for('store.cart'))

@bp.route("/checkout", methods=['GET','POST'])
def checkout(employeeID = 11):
    db = get_db()
    inventoryAmt = db.execute('SELECT inventoryAmount,productID,title FROM Products').fetchall()
    inventory = {}
    titles = {} 
    id = {}
    cart = session.get('cart')
    k = 0
    for i in inventoryAmt:
        id = str(inventoryAmt[k]['productID'])
        amt = int(inventoryAmt[k]['inventoryAmount'])
        title = inventoryAmt[k]['title']
        inventory[id] = amt 
        titles[id] = title
        k+= 1 
    newInventory = {}

    transacFail = False 
    if cart == None:
        transacFail = True 
        error = "You don't have anything to checkout with silly goose!"
    else:
        for i in inventory:
            if inventory[i] <  cart[i]:
                title = titles[i]
                error = f'Sorry we are out of {title}'
                session['cart'][i] = 0
                transacFail = True
                break
            else:
                newInventory[i] = inventory[i]-cart[i]
    if transacFail == False:
        print(session.get('role'))
        if session.get('role') == 'Customer':
            print("I am still a customer")
            flash('You have successfully checked out, Thanks for shopping with us!')
            updateInventory(newInventory,employeeID)
            return redirect(url_for('index'))
        else:
            flash('Inventory Updated')
            updateInventory(newInventory,employeeID)
            return redirect(url_for('store.sale'))
    else: 
        if session.get('role') == 'Customer':
            flash(error)
            return redirect(url_for('index'))
        else:
            flash(error)
            return redirect(url_for('store.sale'))


def updateInventory(newInventory,employeeID):
    print('employeeID')
    print(employeeID)
    db = get_db()
    datetoday = date.today()
    cart = session.get('cart')
    for item in newInventory:
        productID = item
        price = db.execute('SELECT price FROM Products WHERE productID = ?',(productID,)).fetchone()['price']
        db.execute('UPDATE Products SET inventoryAmount = ? WHERE productID = ?',(newInventory[item],item)) 
        db.commit()
        db.execute('INSERT INTO Transactions (date,employeeID, productID, customerID,price, quantity) VALUES (?,?,?,?,?,?)',(datetoday,employeeID,productID,session.get('user_id'),price,cart[item])) 
        db.commit()
    session['cart']  ={'1':0, '2':0, '3':0,'4':0,'5':0,'6':0,'7':0,'8':0,'9':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0}

    return ()


@bp.route("/browse", methods=['GET','POST'])
def browse():
    db = get_db()
    products = db.execute(
        'SELECT productID, title,price FROM Products'
    ).fetchall() 
    genreList = session.get('genreList')
    genre = request.form['genre']
    maxPrice = request.form['maxPrice']
    title = request.form['title']
    if maxPrice == "":
        maxPrice = 0
    try:
        maxPrice = int(maxPrice)
    except:
        error = "Max price must be an integer value greater than 0" 

    if maxPrice <0:
        error = "Max price must be an integer value greater than or equal to 0" 
        flash(error)
        return  redirect(url_for('index'))
    if title != "":
        title ='%'+title+'%'

    if genre != 'select':
        print(genre)
        if title != '':
            print(title)
            if maxPrice > 0:
                products = db.execute('SELECT productID, title,price FROM Products WHERE genreClassification = ? AND title LIKE ? AND price < ?',(genre,title,maxPrice)).fetchall()
            else:products = db.execute('SELECT productID, title,price FROM Products WHERE genreClassification = ? AND title LIKE ?',(genre,title)).fetchall()
        else:    
            if maxPrice > 0:
                print('genre+price')
                products = db.execute('SELECT productID, title,price FROM Products WHERE genreClassification = ? AND price < ?',(genre,maxPrice)).fetchall()
            else:
                print('just genre')
                products = db.execute('SELECT productID, title,price FROM Products WHERE genreClassification = ?',(genre,)).fetchall()
    else:
        if title != '':
            if maxPrice > 0:
                products = db.execute('SELECT productID, title,price FROM Products WHERE title LIKE ? AND price < ?',(title,maxPrice)).fetchall()
            else:
                products = db.execute('SELECT productID, title,price FROM Products WHERE title LIKE ? ',(title,)).fetchall()
        else:
            if maxPrice > 0:
                products = db.execute('SELECT productID, title,price FROM Products WHERE price < ?',(maxPrice,)).fetchall()
            else:
                products = db.execute('SELECT productID, title,price FROM Products').fetchall()

    return  render_template('store/index.html', products=products, genreList = genreList)


@bp.route('/salesview', methods=['GET','POST'])
def salesview():
    print(session.get('jobTitle'))
    db = get_db()
    session.get('genreList', [])
    genre = db.execute('SELECT DISTINCT genreClassification FROM Products').fetchall()
    genreList = []
    for a in genre:
        genreList.append(a['genreClassification'])
    genreList.append('select')
    session['genreList'] = genreList
    products = db.execute(
        'SELECT productID, title,price FROM Products'
    ).fetchall() 
    print(session.get('jobTitle'))
    return render_template('store/sales.html', products=products, genreList = genreList,role = session.get('jobTitle'))


@bp.route('/sale', methods=['GET','POST'])
def sale():
    print('sale is happening')
    db = get_db()
    user_id = session.get('user_id')
    print('userID')
    print(user_id)
    products = db.execute(
        'SELECT productID, title,price FROM Products'
    ).fetchall() 
    cart = session.get('cart', {'1':0, '2':0, '3':0,'4':0,'5':0,'6':0,'7':0,'8':0,'9':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0})
    for product in products:
        id = str(product['productID'])
        rformname = f"quantity{id}"
        try:
            cart[id] = int(request.form[rformname])
        except:
            flash('Please enter integer values for items')
    session['cart'] = cart
    print('look at me ')
    print(cart)
    checkout(user_id)
    return render_template('store/sales.html', products=products)



@bp.route('/bookstats', methods=['GET','POST'])
def bookstats():
    db = get_db()

    productSalesList = {}
    productSales = db.execute('SELECT products.productID as productID, products.title, SUM(Transactions.quantity) AS totalSales, SUM(products.price * transactions.quantity) AS totalProfit FROM Transactions inner Join products on products.productID = Transactions.productID GROUP BY products.productID Order By totalProfit DESC;').fetchall()
    for product in productSales:
        productSalesList[product['productID']] = [product['title'],product['totalProfit']]

    productQuantList = {}
    productQuant = db.execute('SELECT products.productID as productID, products.title, SUM(Transactions.quantity) AS totalSales FROM Transactions inner Join products on products.productID = Transactions.productID GROUP BY products.productID Order By totalSales DESC;').fetchall()
    for product in productQuant:
        productQuantList[product['productID']] = [product['title'],product['totalSales']]

    genreList = {}
    genreClass = db.execute('SELECT genreClassification, SUM(quantity) AS totalSales FROM Transactions JOIN Products ON Transactions.productID = Products.productID GROUP BY genreClassification ORDER BY totalSales DESC; ').fetchall()
    for genre in genreClass:
        genreList[genre['genreClassification']] =genre['totalSales']

    return render_template('store/stats1.html', productSalesList = productSalesList,productQuantList = productQuantList,genreList = genreList)

@bp.route('/workstats', methods=['GET','POST'])
def workstats():
    db = get_db()

    transactionList = {}
    transactions = db.execute('SELECT * from Transactions Join Salespersons on salespersons.employeeID = Transactions.employeeID').fetchall()
    for item in transactions:
        if item['quantity'] > 0:
            transactionList[item['ordernumber']] =(item['name'],item['customerID'],item['productID'],item['storeAssigned'])

    print(session.get('user_id'))
    print(transactionList)
    regionSalesList = {}
    regionSales = db.execute('SELECT Region.regionName, SUM(price * quantity) AS totalSales FROM SalesPersons JOIN Transactions ON Transactions.employeeID = salespersons.employeeID JOIN Store ON Salespersons.storeAssigned = store.storeID JOIN region on store.regionID = region.regionID GROUP BY Region.regionID;').fetchall() 
    for region in regionSales:
        regionSalesList[region['regionName']] = region['totalSales']
    print(regionSalesList)
    employeeSalesList = {}
    employeeSales = db.execute('SELECT salespersons.name as name, SUM(price * quantity) AS totalSales From SalesPersons Join Transactions on Transactions.employeeID = Salespersons.employeeID Group BY salespersons.employeeID ORDER BY totalSales DESC').fetchall()
    for employee in employeeSales:
        employeeSalesList[employee['name']] = employee['totalSales']
    print(employeeSalesList)

    return render_template('store/stats2.html', regionSalesList = regionSalesList, employeeSalesList = employeeSalesList)


@bp.route('/inventory', methods=['GET','POST'])
def inventory():
    db = get_db()

    productQuantList = {}
    products = db.execute('SELECT * from products' ).fetchall()
    for item in products:
        productQuantList[item['productID']] = (item['title'],item['inventoryAmount'])
    return render_template('store/inventory.html', products = productQuantList)


@bp.route('/manager', methods=['GET','POST'])
def manager():
    db = get_db()
    employees = db.execute('SELECT * from Salespersons').fetchall()
    print(employees[0]['employeeID'])
    productQuantList = {}
    products = db.execute('SELECT * from products' ).fetchall()
    regions = db.execute('SELECT * from region' ).fetchall()
    return render_template('store/manager.html', products = products,employees=employees,regions=regions)


@bp.route('/removeEmployee', methods=['GET','POST'])
def removeEmployee():
    print('remove')
    db = get_db()
    print(request.form['employeeID'])
    employeeID = request.form['employeeID']
    users = db.execute('SELECT * from user').fetchall()
    employees = db.execute('SELECT * from Salespersons').fetchall()

    userlist = {}
    for user in users:
       userlist[user['id']] = (user['username'])
    print(userlist)
    employeeList = {} 
    print('employees')
    for employee in employees:
       employeeList[employee['employeeid']] = (employee['name'])
    print(employeeList)

    #db.execute('PRAGMA foreign_keys = ON;')

    db.execute('DELETE FROM user WHERE id = ?;',(employeeID,))
    db.commit()

    return redirect(url_for('store.manager'))

@bp.route('/editInventory', methods=['GET','POST'])
def editInventory():
    print(request.form)
    db = get_db()
    products = db.execute('SELECT * from products').fetchall()
    for product in products:
        id = product['productID']
        rformname = f"quantity{id}"
        amount= int(request.form[rformname])
        db.execute('UPDATE Products SET inventoryAmount = ? WHERE productID = ?',(amount,id))
        db.commit()
    return redirect(url_for('store.manager'))



@bp.route('/removeProduct', methods=['GET','POST'])
def removeProduct():
    print('remove')
    db = get_db()
    print('request')
    print(request.form['productID'])
    productID = request.form['productID']
    print(productID)
    products = db.execute('SELECT * from products WHERE productID = ?', (productID,)).fetchall()
    print('products')
    print(products)
    #db.execute('PRAGMA foreign_keys = ON;')

    db.execute('DELETE FROM Products WHERE productid = ?;',(productID,))
    db.commit()

    return redirect(url_for('store.manager'))


@bp.route('/addProduct', methods=['GET','POST'])
def addProduct():
    print('add')
    db = get_db()
    title = request.form['title']
    inventory = request.form['inventory']
    price = request.form['price']
    genre = request.form['genre']
    author = request.form['author']
    try:
        db.execute("INSERT INTO Products (title, author,inventoryAmount,price,genreClassification) VALUES (?, ?,?,?,?)",
                    (title, author,inventory, price,genre),
                )
        db.commit()
    except:
        flash("Sorry there was an error")
    return redirect(url_for('store.manager'))


@bp.route('/addStore', methods=['GET','POST'])
def addStore():
    print('add')
    db = get_db()
    address = request.form['address']
    print(address)
    manager = db.execute('SELECT employeeID from SalesPersons WHERE name = ?',(request.form['manager'],)).fetchone()['employeeid']
    print(manager)
    num= request.form['num']
    print(num)
    regionID = request.form['regionID']
    print(regionID)
    try:
        db.execute("INSERT INTO Store (address, manager,numberofSalespersons,regionID) VALUES (?, ?,?,?);",
                    (address, manager, num,regionID),
                )
        db.commit()
        print('gotit')
    except:
        flash("Sorry there was an error")
    return redirect(url_for('store.manager'))



@bp.route('/orders', methods=['GET','POST'])
def orders():
    db = get_db()
    orders = db.execute('SELECT * from Transactions Join products ON  products.productID = Transactions.productID where customerID = ?',(session.get('user_id'),)).fetchall()
    for order in orders:
        print(order['ordernumber'])
    return render_template('store/orders.html', orders=orders)





