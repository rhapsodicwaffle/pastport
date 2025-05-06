from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from models import Capsule, db, User, Bookmark, Notification
from werkzeug.security import generate_password_hash

home = Blueprint('home', __name__)


@home.route('/home')

def homepage():
    public_capsules = Capsule.query.filter_by(accessibility='public').order_by(Capsule.created_at.desc()).all()

    bookmarked_ids = set()
    if 'user' in session:
        bookmarks = Bookmark.query.filter_by(user_id=session['user'], item_type='capsule').all()
        bookmarked_ids = set(b.item_id for b in bookmarks)

    return render_template('home.html', capsules=public_capsules, bookmarked_ids=bookmarked_ids)


@home.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')
    user_data = User.query.filter_by(username=session['user']).first()
    return render_template('profile.html', user=user_data)

@home.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        return redirect('/login')
    
    user_data = User.query.filter_by(username=session['user']).first()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if email:
            user_data.email = email
        if password and password == confirm_password:
            user_data.password = generate_password_hash(password)

        db.session.commit()
        flash("Profile updated.")
        return redirect(url_for('home.profile'))

    return render_template('edit_profile.html', user=user_data)

@home.route('/delete-account', methods=['POST'])
def delete_account():
    if 'user' not in session:
        return redirect('/login')
    
    user_data = User.query.filter_by(username=session['user']).first()
    db.session.delete(user_data)
    db.session.commit()
    session.clear()
    flash("Your account has been deleted.")
    return redirect('/signup')

@home.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect('/login')


@home.route('/notifications')
def notifications():
    if 'user' not in session:
        return redirect('/login')

    user_data = User.query.filter_by(username=session['user']).first()
    notifications = Notification.query.filter_by(user_id=user_data.username).order_by(Notification.created_at.desc()).all()

    return render_template('notifications.html', notifications=notifications)
