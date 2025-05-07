from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Capsule, Like, Notification, Bookmark, File, db
from datetime import datetime

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats')
@login_required
def show_stats():
    username = current_user.username

    # Capsule Statistics
    total_capsules = Capsule.query.filter_by(owner_username=username).count()
    encrypted_capsules = Capsule.query.filter_by(owner_username=username, type='encrypted').count()
    public_capsules = Capsule.query.filter_by(owner_username=username, accessibility='public').count()
    private_capsules = Capsule.query.filter_by(owner_username=username, accessibility='private').count()
    expired_capsules = Capsule.query.filter(
        Capsule.owner_username == username,
        Capsule.expiry_date < db.func.current_date()
    ).count()

    # Interaction Statistics
    likes_received = Like.query.join(Capsule).filter(Capsule.owner_username == username).count()
    unread_notifications = Notification.query.filter_by(user_id=username, read=False).count()
    bookmarks_count = Bookmark.query.filter_by(user_id=username, item_type='capsule').count()

    # Views (If you store them in a `views` field)
    total_views = Capsule.query.filter_by(owner_username=username).with_entities(db.func.sum(Capsule.views)).scalar() or 0

    # Downloads (Assuming you track them with the `File` model)
    total_downloads = File.query.join(Capsule).filter(Capsule.owner_username == username).count()

    # Last Opened (Optional, you can set this up to track the last time a capsule was opened)
    last_opened = datetime.utcnow().strftime("%Y-%m-%d at %H:%M:%S UTC")  # Placeholder

    return render_template(
        'stats.html',
        total_capsules=total_capsules,
        encrypted_capsules=encrypted_capsules,
        public_capsules=public_capsules,
        private_capsules=private_capsules,
        expired_capsules=expired_capsules,
        likes_received=likes_received,
        unread_notifications=unread_notifications,
        bookmarks_count=bookmarks_count,
        total_views=total_views,
        total_downloads=total_downloads,
        last_opened=last_opened
    )
