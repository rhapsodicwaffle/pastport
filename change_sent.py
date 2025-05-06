from flask import Flask
from models import db, Capsule

# Initialize the Flask app
app = Flask(__name__)

# Set up your app configuration for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capsule.db'  # Replace with your actual DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Function to update the sent status of a capsule
def update_sent_status(capsule_id, new_sent_status):
    with app.app_context():  # Create an app context for database operations
        capsule = Capsule.query.get(capsule_id)  # Retrieve the capsule by ID
        
        if capsule:
            # Update the sent status
            capsule.sent = new_sent_status
            db.session.commit()  # Commit the changes to the database
            print(f"Capsule {capsule.id} sent status updated to {new_sent_status}.")
        else:
            print(f"Capsule with ID {capsule_id} not found.")

if __name__ == '__main__':
    capsule_id = 9  # Take capsule ID as input
    new_sent_status = False  # True or False
    update_sent_status(capsule_id, new_sent_status)  # Call the function to update the sent status
