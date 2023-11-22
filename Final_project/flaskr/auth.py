import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    print("register")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        db = get_db()
        error = None
        print('uh')
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not role:
            error = 'Role is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password,role,infodone) VALUES (?, ?,?,?)",
                    (username, generate_password_hash(password), role,"no"),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    print("login")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()


        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            if user['infodone'] == "no" and user['role'] == "Customer":
                return redirect(url_for("auth.info"))
            else:
                 return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/info', methods=('GET', 'POST'))
def info():
    print("getinfo")
    db = get_db()
    error = None
    user_id = session.get('user_id')
    if request.method == 'POST':
        name = request.form['fullName']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        zipCode = request.form['zipCode']
        customerType = request.form['customerType']
        marriageStatus = request.form['marriageStatus']
        gender = request.form['gender']
        age = request.form['age']
        income = request.form['income']
        businessCategory = request.form['businessCategory']
        businessIncome = request.form['businessIncome']
        print("sigh")

        if state == "select":
            error = "Please select a state"
        if customerType == "Business" and ( not businessCategory  or not businessIncome):
            error = 'Businesses must report a Business Category and Business Income'
        if customerType == "Home" and (marriageStatus == "select" or not gender or not age or  not income):
            error = 'Individuals must report a marital status, gender, age, and income'

        if error is None:
                try:
                    db.execute(
                        "UPDATE user SET infodone = ? WHERE id = ?", ("yes",user_id)
                    )
                    db.commit()
                    db.execute(

                    "INSERT INTO  Customers(customerID,name,street,city,state,zipCode,kind,marriageStatus,gender,age,income,businessCategory,companyGrossAnnualIncome) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (user_id,name,street,city,state,zipCode,customerType,marriageStatus,gender,age,income,businessCategory,businessIncome)
                    )
                    db.commit()
                except db.IntegrityError:
                   error = f"User {username} is already registered."
                else:
                    return redirect(url_for('index'))
        flash(error)


    return render_template('auth/info.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view