from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from models import db, Capsule, BlogPost, Bookmark

bookmark_bp = Blueprint('bookmark', __name__)

# Bookmark an item (capsule or blog)
@bookmark_bp.route('/bookmark/<item_type>/<int:item_id>', methods=['POST'])
def add_bookmark(item_type, item_id):
    if 'user' not in session:
        flash("Login required to bookmark.")
        return redirect(url_for('auth.login'))

    # Prevent duplicate bookmarks
    existing = Bookmark.query.filter_by(user_id=session['user'], item_type=item_type, item_id=item_id).first()
    if not existing:
        new = Bookmark(user_id=session['user'], item_type=item_type, item_id=item_id)
        db.session.add(new)
        db.session.commit()
        flash("Bookmarked successfully.")
    else:
        flash("Already bookmarked.")

    return redirect(request.referrer or url_for('home.homepage'))

# Remove a bookmark
@bookmark_bp.route('/unbookmark/<item_type>/<int:item_id>', methods=['POST'])
def remove_bookmark(item_type, item_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    bookmark = Bookmark.query.filter_by(user_id=session['user'], item_type=item_type, item_id=item_id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        flash("Bookmark removed.")

    return redirect(request.referrer or url_for('bookmark.view_bookmarks'))

# View all bookmarks
@bookmark_bp.route('/bookmarks')
def view_bookmarks():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    capsule_ids = [b.item_id for b in Bookmark.query.filter_by(user_id=session['user'], item_type='capsule').all()]
    blog_ids = [b.item_id for b in Bookmark.query.filter_by(user_id=session['user'], item_type='blog').all()]

    capsules = Capsule.query.filter(Capsule.id.in_(capsule_ids)).all()
    blogs = BlogPost.query.filter(BlogPost.id.in_(blog_ids)).all()

    return render_template('bookmarks.html', capsules=capsules, blogs=blogs)
