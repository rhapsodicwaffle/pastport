import os
from flask import Flask
from flask_socketio import SocketIO
from flask_migrate import Migrate
from models import db
from routes.collab import collab, register_socketio_handlers
from routes.auth import auth
from routes.capsule import capsule
from routes.home import home
from routes.delete_expired_capsules import delete_expired_capsules
from routes.blog import blog  
from routes.bookmark import bookmark_bp
from routes.stats import stats_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = os.urandom(24).hex()

db.init_app(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(auth)
app.register_blueprint(capsule)
app.register_blueprint(home)
app.register_blueprint(blog)
app.register_blueprint(bookmark_bp)
app.register_blueprint(collab)
app.register_blueprint(stats_bp)
register_socketio_handlers(socketio)

@app.route('/')
def index():
    return "<h1>Welcome to PastPort API</h1><p>Visit /login or /create to get started.</p>"

@app.route('/run-delete-expired')
def run_delete_expired():
    # Optional: Add a secret token check for security
    token = request.args.get('token')
    if token != 'my_secret_token':
        return "Unauthorized", 401

    delete_expired_capsules()
    return "Expired capsules deleted successfully!"

if __name__ == '__main__':
    with app.app_context():
        delete_expired_capsules()
    app.run(debug=True)
