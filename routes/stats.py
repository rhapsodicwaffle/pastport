from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Capsule, Like, Notification, db

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats')
@login_required
def show_stats():
    username = current_user.username

    # Fetch stats relevant to the user
    total_capsules = Capsule.query.filter_by(owner_username=username).count()
    encrypted_capsules = Capsule.query.filter_by(owner_username=username, type='encrypted').count()
    public_capsules = Capsule.query.filter_by(owner_username=username, accessibility='public').count()
    private_capsules = Capsule.query.filter_by(owner_username=username, accessibility='private').count()
    expired_capsules = Capsule.query.filter(
        Capsule.owner_username == username,
        Capsule.expiry_date < db.func.current_date()
    ).count()
    likes_received = Like.query.join(Capsule).filter(Capsule.owner_username == username).count()
    unread_notifications = Notification.query.filter_by(user_id=username, read=False).count()

    return render_template(
        'stats.html',
        total_capsules=total_capsules,
        encrypted_capsules=encrypted_capsules,
        public_capsules=public_capsules,
        private_capsules=private_capsules,
        expired_capsules=expired_capsules,
        likes_received=likes_received,
        unread_notifications=unread_notifications
    )
