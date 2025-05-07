from flask import Blueprint, render_template
from models import db, Capsule, Bookmark, Like, File, Notification
from datetime import datetime

# Create the stats Blueprint
stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats')
def stats():
    user = current_user.username

    total_views = Capsule.query.filter_by(owner_username=user).count()
    bookmarks_count = Bookmark.query.filter_by(user_id=user).count()

    total_downloads = File.query.join(Capsule).filter(Capsule.owner_username == user).count()
    likes_received = Like.query.filter_by(user_id=user).count()


    unread_notifications = Notification.query.filter_by(user_id=user, read=False).count()
    last_opened = Capsule.query.filter_by(owner_username=user).order_by(Capsule.created_at.desc()).first()

    return render_template(
        'stats.html',
        total_views=total_views,
        bookmarks_count=bookmarks_count,
        total_downloads=total_downloads,
        likes_received=likes_received,
        unread_notifications=unread_notifications,
        last_opened=last_opened.created_at if last_opened else 'N/A'
    )
