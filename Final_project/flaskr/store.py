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
def checkout():
    print('checkout')
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
    print(inventory)
    newInventory = {}
    transacFail = False 
    for i in inventory:
        print(k)
        if inventory[i] <  cart[i]:
            title = titles[i]
            error = f'Sorry we are out of {title}'
            print(error)
            transacFail = True
            break
        else:
            newInventory[i] = inventory[i]-cart[i]
    if transacFail == False:
        session['cart']  ={'1':0, '2':0, '3':0,'4':0,'5':0,'6':0,'7':0,'8':0,'9':0,'10':0,'11':0,'12':0,'13':0,'14':0,'15':0}
        flash('You have successfully checked out, Thanks for shopping with us!')
        updateInventory(newInventory)
        return redirect(url_for('index'))
    else: 
        flash(error)
        return redirect(url_for('store.cart'))


def updateInventory(newInventory):
    db = get_db()
    salesPerson = 'Maddie'
    datetoday = date.today()
    for item in newInventory:
        productID = item
        price = db.execute('SELECT price FROM Products WHERE productID = ?',(productID,)).fetchone()['price']
        db.execute('UPDATE Products SET inventoryAmount = ? WHERE productID = ?',(newInventory[item],item)) 
        db.commit()
        db.execute('INSERT INTO Transactions (date,salespersonName, productID, customerID,price, quantity) VALUES (?,?,?,?,?,?)',(datetoday,salesPerson,productID,session.get('user_id'),price,newInventory[item])) 
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