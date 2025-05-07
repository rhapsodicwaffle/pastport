from flask import Blueprint, render_template
from models import db, Capsule, Bookmark, Like, File, Notification
from datetime import datetime

# Create the stats Blueprint
stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats')
def stats():
    # Assuming you have the current_user (e.g., from Flask-Login)
    user = current_user.username  # Replace with actual authentication logic
    
    # 1. Views: Count the capsules owned by the user
    total_views = Capsule.query.filter_by(owner_username=user).count()
    
    # 2. Bookmarks: Count the bookmarks for this user
    bookmarks_count = Bookmark.query.filter_by(user_id=user).count()

    # 3. Downloads: Count the files associated with capsules owned by the user
    total_downloads = File.query.join(Capsule).filter(Capsule.owner_username == user).count()

    # 4. Likes: Count how many likes the user received for their capsules
    likes_received = Like.query.join(Capsule).filter(Capsule.owner_username == user).count()

    # 5. Unread Notifications: Count how many notifications are unread
    unread_notifications = Notification.query.filter_by(user_id=user, read=False).count()

    # 6. Last Opened: Get the latest capsule (based on created_at) opened by the user
    last_opened = Capsule.query.filter_by(owner_username=user).order_by(Capsule.created_at.desc()).first()

    # Format last opened timestamp if available
    last_opened_time = last_opened.created_at if last_opened else 'N/A'

    # Render the stats page and pass the data to the template
    return render_template(
        'stats.html',
        total_views=total_views,
        bookmarks_count=bookmarks_count,
        total_downloads=total_downloads,
        likes_received=likes_received,
        unread_notifications=unread_notifications,
        last_opened_time=last_opened_time
    )
