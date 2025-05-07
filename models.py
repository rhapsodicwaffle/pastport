from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class User(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Capsule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_username = db.Column(db.String(100), db.ForeignKey('user.username'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.Date, nullable=True)
    delivery_date = db.Column(db.Date, nullable=True)
    sent = db.Column(db.Boolean, default=False)
    encryption = db.Column(db.String(50), default='N/A')
    type = db.Column(db.String(50))
    accessibility = db.Column(db.String(20), default='private')
    text = db.Column(db.Text)
    tags = db.Column(db.String(255))
    recipient_email = db.Column(db.String(120))
    files = db.relationship('File', backref='capsule', lazy=True)
    title = db.Column(db.String(100), nullable=False)
    is_memorial = db.Column(db.Boolean, default=False)
    verifier_emails = db.Column(JSON, nullable=True)  # list of verifier emails
    verifier_confirmations = db.Column(JSON, nullable=True)  # list of confirmed emails
    recipient_emails = db.Column(JSON, nullable=True)  # list of recipients
    views = db.Column(db.Integer, default=0)  # Track views

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    capsule_id = db.Column(db.Integer, db.ForeignKey('capsule.id'))
    downloads = db.Column(db.Integer, default=0)  # Track downloads

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    item_type = db.Column(db.String, nullable=False)  # 'capsule' or 'blog'
    item_id = db.Column(db.Integer, nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capsule_id = db.Column(db.Integer, db.ForeignKey('capsule.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    capsule = db.relationship('Capsule', backref='likes', lazy=True)
    user = db.relationship('User', backref='liked_capsules', lazy=True)

    def __repr__(self):
        return f'<Like {self.user_id} on Capsule {self.capsule_id}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)  # Recipient
    capsule_id = db.Column(db.Integer, db.ForeignKey('capsule.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False)  # Whether the notification is read
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')
    capsule = db.relationship('Capsule', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.message}>'

class CollaborativeMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(8), nullable=False)  # Room ID to associate the message
    username = db.Column(db.String(100), nullable=False)  # Username of the user who sent the message
    message = db.Column(db.Text, nullable=False)  # The message content
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Time the message was sent

    def __repr__(self):
        return f"<CollaborativeMessage room_id={self.room_id} username={self.username} message={self.message}>"
