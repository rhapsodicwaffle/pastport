from flask import Flask
from flask_socketio import SocketIO
from routes.collab import collab, register_socketio_handlers
from flask_sqlalchemy import SQLAlchemy
from models import db
from routes.auth import auth
from routes.capsule import capsule
from routes.home import home
from routes.delete_expired_capsules import delete_expired_capsules
from routes.blog import blog  
from routes.bookmark import bookmark_bp
import config

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(auth)
app.register_blueprint(capsule)
app.register_blueprint(home)
app.register_blueprint(blog)
app.register_blueprint(bookmark_bp)
app.register_blueprint(collab)
# Register socketio events
register_socketio_handlers(socketio)  # ✅ Hook up real-time events


@app.route('/')
def index():
    return "<h1>Welcome to PastPort API</h1><p>Visit /login or /create to get started.</p>"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        delete_expired_capsules()
    app.run(debug=True)

