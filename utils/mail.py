import os
import yagmail
import os
import sys
import yagmail
import jwt
from flask import Flask
from flask import url_for
from flask import current_app
from models import db



SENDER_EMAIL = "mir.md.mohiuddinabrar@g.bracu.ac.bd"
APP_PASSWORD = "tuth uxun joud mgwr"

yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)

def send_capsule_email(to_email, message_text, filenames):
    attachments = []
    for fn in filenames:
        if fn:  # check filename is not empty
            full_path = os.path.join("static", "uploads", fn)
            if os.path.isfile(full_path):  # only if the file actually exists
                attachments.append(full_path)

    yag.send(
        to=to_email,
        subject="🎁 Your Capsule Has Arrived",
        contents=message_text,
        attachments=attachments if attachments else None  # if no attachments, don't send blank paths
    )
def send_verification_emails(capsule):
    for verifier_email in capsule.verifier_emails:
        token = create_verifier_token(capsule.id, verifier_email)
        verify_link = url_for('capsule.verify_death', token=token, _external=True)
        subject = "⚰️ Confirm Death Verification Request"
        body = f"""
        Dear Verifier,

        Someone has listed you as a verifier for a memorial capsule.

        Please confirm the person's death by clicking the link below:
        {verify_link}

        Thank you for your support.
        """
        yag.send(
            to=verifier_email,
            subject=subject,
            contents=body
        )

# Function to create secure token
def create_verifier_token(capsule_id, verifier_email):
    payload = {
        'capsule_id': capsule_id,
        'verifier_email': verifier_email
    }
    token = jwt.encode(payload,current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Function to decode the secure token
def decode_verifier_token(token):
    try:
        payload = jwt.decode(token,current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    
def send_email(to, subject, body):
    yag.send(
        to=to,
        subject=subject,
        contents=body
    )

def deliver_memorial_capsule(capsule):
    # Check if there are recipient emails
    if not capsule.recipient_emails:
        print(f"No recipient emails for capsule {capsule.id}.")
        return

    print(f"Delivering memorial capsule {capsule.id}...")  # Add this line to check if the function runs
    
    subject = f"🎁 Memorial Capsule: {capsule.title}"
    body = f"""
    Dear Recipient,

    This is a memorial capsule left by {capsule.owner_username}.

    Message:
    {capsule.text}

    Regards,
    Time Capsule Team
    """

    # If capsule has files, add them to the attachments list
    filenames = [file.filename for file in capsule.files] if capsule.files else []

    # Send the email to each recipient
    for recipient_email in capsule.recipient_emails:
        try:
            send_capsule_email(
                to_email=recipient_email,
                message_text=body,
                filenames=filenames
            )
            print(f"Capsule {capsule.id} delivered to {recipient_email}.")  # Print for successful delivery
        except Exception as e:
            # Handle any errors during email sending
            print(f"Failed to send capsule {capsule.id} to {recipient_email}: {str(e)}")

    # Mark capsule as sent and commit the changes
    capsule.sent = True
    db.session.commit()
    print(f"Capsule {capsule.id} marked as 'sent'.")  # Print to confirm changes committed


