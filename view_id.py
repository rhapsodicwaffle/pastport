from flask import Flask
from models import db, Capsule

# Initialize Flask app
app = Flask(__name__)

# Set the SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capsule.db'  # Adjust the path as needed

# Initialize the database
db.init_app(app)

with app.app_context():  # Use app context to access the database
    # Query all capsules and get their IDs
    capsules = Capsule.query.all()

    # Print each capsule's ID
    print("Capsule IDs in the database:")
    for capsule in capsules:
        print(capsule.id)
