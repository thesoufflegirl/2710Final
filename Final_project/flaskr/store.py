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
    cart = session.get('cart')
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
def checkout(employeeID = 6):
    db = get_db()
    inventoryAmt = db.execute('SELECT inventoryAmount,productID,title FROM Products').fetchall()
    inventory = {}
    titles = {} 
    id = {}
    cart = session.get('cart')
    print(cart)
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
    for i in inventory:
        if inventory[i] <  cart[i]:
            title = titles[i]
            error = f'Sorry we are out of {title}'
            transacFail = True
            break
        else:
            newInventory[i] = inventory[i]-cart[i]
    if transacFail == False:
        if session.get('role') == 'Customer':
            flash('You have successfully checked out, Thanks for shopping with us!')
            updateInventory(newInventory,employeeID)
            return redirect(url_for('index'))
        else:
            flash('Inventory Updated')
            updateInventory(newInventory,employeeID)
            return redirect(url_for('store.sale'))
        session['cart']  ={'1':0, '2':0, '3':0,'4':0,'5':0,'6':0,'7':0,'8':0,'9':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0}

    else: 
        if session.get('role') == 'Customer':
            flash(error)
            return redirect(url_for('index'))
        else:
            flash(error)
            return redirect(url_for('store.sale'))


def updateInventory(newInventory,employeeID):
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
    return render_template('store/sales.html', products=products, genreList = genreList)


@bp.route('/sale', methods=['GET','POST'])
def sale():
    print('sale is happening')
    db = get_db()
    user_id = session.get('user_id')
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
    productSales = db.execute('SELECT products.productID as productID, products.title, SUM(Transactions.quantity) AS totalSales, SUM(products.price * transactions.quantity) AS totalProfit FROM Transactions inner Join products on products.productID = Transactions.productID GROUP BY products.productID;').fetchall()
    for product in productSales:
        productSalesList[product['productID']] = [product['title'],product['totalProfit']]

    productQuantList = {}
    productQuant = db.execute('SELECT products.productID as productID, products.title, SUM(Transactions.quantity) AS totalSales FROM Transactions inner Join products on products.productID = Transactions.productID GROUP BY products.productID;').fetchall()
    for product in productQuant:
        productQuantList[product['productID']] = [product['title'],product['totalSales']]

    return render_template('store/stats1.html', productSalesList = productSalesList,productQuantList = productQuantList)
