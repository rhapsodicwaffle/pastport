from flask import Flask
from models import db, Capsule
from utils.mail import send_capsule_email  # Assuming this is where the function is defined
import os
import sys

# Initialize Flask app
app = Flask(__name__)

# Set the SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capsule.db'  # Adjust the path as needed

# Initialize the database
db.init_app(app)


def deliver_memorial_capsule(capsule):
    # Check if any verifier has confirmed (we assume 1 confirmation is enough)
    print(f"{capsule.verifier_confirmations} is being processed...")  # Check if the function runs
    if not capsule.verifier_confirmations:  # Check if there is at least one confirmation
        print(f"Capsule {capsule.id} has no verifications yet. Skipping delivery.")
        return
    
    if capsule.verifier_emails and capsule.verifier_confirmations:
        # Check for unconfirmed verifiers
        unconfirmed_verifiers = [
            email for email in capsule.verifier_emails if email not in capsule.verifier_confirmations
        ]
        
        # If there are unconfirmed verifiers, skip the delivery
    
    # Check if there are recipient emails
    if not capsule.recipient_emails:
        print(f"No recipient emails for capsule {capsule.id}.")
        return

    print(f"Delivering memorial capsule {capsule.id}...")  # Check if the function runs
    
    subject = f"🎁 Memorial Capsule: {capsule.title}"
    body = f"""
    Dear Recipient,

    This is a memorial capsule left by {capsule.owner_username}.

    Message:
    {capsule.text}

    Regards,
    Time Capsule Team
    """

    filenames = [file.filename for file in capsule.files] if capsule.files else []

    # Loop through each recipient email and send the email
    for recipient_email in capsule.recipient_emails:
        try:
            send_capsule_email(
                to_email=recipient_email,
                message_text=body,
                filenames=filenames
            )
            print(f"Capsule {capsule.id} delivered to {recipient_email}.")
        except Exception as e:
            print(f"Failed to send capsule {capsule.id} to {recipient_email}: {str(e)}")

    # Mark capsule as sent and commit changes to the database
    capsule.sent = True
    db.session.commit()
    print(f"Capsule {capsule.id} marked as 'sent'.")


# Function to send all unsent capsules (with verification check)
def send_unsent_capsules():
    with app.app_context():  # Use app context for database operations
        # Query all unsent capsules
        unsent_capsules = Capsule.query.filter_by(sent=False).all()

        # Loop through each unsent capsule and deliver it
        for capsule in unsent_capsules:
            print(f"{capsule.verifier_confirmations}")
            print(f"Processing capsule with ID {capsule.id}...")

            # Check if any verifier has not confirmed
            if capsule.verifier_emails and capsule.verifier_confirmations:
                unconfirmed_verifiers = [
                    email for email in capsule.verifier_emails if email not in capsule.verifier_confirmations
                ]

                # If there are unconfirmed verifiers, skip delivery (you may modify this logic)
                print(unconfirmed_verifiers)
                if len(unconfirmed_verifiers) > 2:  # If there is at least one unconfirmed verifier
                    print(f"Capsule {capsule.id} has unconfirmed verifiers: {', '.join(unconfirmed_verifiers)}. Skipping delivery.")
                    continue  # Skip delivery if there are unconfirmed verifiers

            # Proceed with delivery if any verifier has confirmed
            deliver_memorial_capsule(capsule)


if __name__ == '__main__':
    send_unsent_capsules()  # Run the function to send all unsent capsules
