from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            return "Email already exists!"
        if User.query.filter_by(username=username).first():
            return "Username already taken!"

        user = User(email=email, password=password, username=username)
        db.session.add(user)
        db.session.commit()
        session['user'] = username
        return redirect('/home')

    return render_template('signup.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            return redirect('/home')
        else:
            return "Invalid email or password!"
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')
