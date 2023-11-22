from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('store', __name__)


#cart = session['cart']

@bp.route('/', methods=['GET','POST'])
def index():
    db = get_db()
    products = db.execute(
        'SELECT productID, title,price FROM Products'
    ).fetchall() 
    if request.method == 'POST':
        print('blah')
        #quantity = request.form['quantity']
        #print(quantity)
    return render_template('store/index.html', products=products)

@bp.route('/cart', methods=('GET', 'POST'))
def cart():
    return 4

@login_required


@bp.route("/add", methods=['GET','POST'])
def add():
    print('add')
    return redirect(url_for('index'))

    #if cart in session:
     #   cart = cart.add(product=request.form['product'], quantity=int(request.form['quantity']))
      #  print(cart)
    #else:
    #    cart = session.get('cart', {'1':0, '2':0, '3':0})
    #    print(cart, "new")
    #    cart = cart.add(product=request.form['product'], quantity=int(request.form['quantity']))

    #return jsonify(cart)
