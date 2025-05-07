from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Capsule, Like, Notification, File,User
from utils.mail import send_capsule_email,send_verification_emails,decode_verifier_token,send_email
from datetime import datetime, date
from werkzeug.utils import secure_filename
import os
from flask import Blueprint, request, redirect, url_for, session, flash


capsule = Blueprint('capsule', __name__)

@capsule.route('/create', methods=['GET', 'POST'])
def create():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        owner_username = session['user']
        title = request.form['title']
        text = request.form['text']
        capsule_type = request.form['type']
        accessibility = request.form['accessibility']
        encryption = request.form.get('encryption') or 'N/A'
        expiry_str = request.form.get('expiry_date')
        tags = request.form.get('tags', '')
        send_now = request.form.get('send_now')
        schedule_str = request.form.get('schedule_date')

        # Handle expiry_date
        try:
            expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date() if expiry_str else None
        except:
            expiry_date = None

        # Handle delivery date
        try:
            delivery_date = date.today() if send_now else datetime.strptime(schedule_str, "%Y-%m-%d").date()
        except:
            delivery_date = None

        # Only for share type
        recipient_email = request.form.get('recipient_email') if accessibility == 'share' else None
        send_email_now = bool(send_now and accessibility == 'share' and recipient_email)

        # Handle memorial capsule fields
        is_memorial = bool(request.form.get('is_memorial'))
        if is_memorial:
            verifiers = [
                request.form.get('verifier1'),
                request.form.get('verifier2'),
                request.form.get('verifier3')
            ]
            recipients = [
                request.form.get('recipient1'),
                # add more if needed
            ]
        else:
            verifiers = []
            recipients = []

        # Create the capsule
        capsule = Capsule(
            title=title,
            owner_username=owner_username,
            text=text,
            type=capsule_type,
            accessibility=accessibility,
            encryption=encryption,
            expiry_date=expiry_date,
            tags=tags,
            recipient_email=recipient_email,
            delivery_date=delivery_date,
            sent=send_email_now,
            is_memorial=is_memorial,
            verifier_emails=verifiers,
            verifier_confirmations=[],
            recipient_emails=recipients
        )

        db.session.add(capsule)
        db.session.commit()

        # Handle uploaded files
        uploaded_files = request.files.getlist("files")
        upload_path = os.path.join("static", "uploads")
        os.makedirs(upload_path, exist_ok=True)

        for file in uploaded_files:
            if file and '.' in file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)
                db.session.add(File(filename=filename, capsule_id=capsule.id))

        db.session.commit()

        # Send memorial verification emails if needed
        if is_memorial:
            send_verification_emails(capsule)

        # Email immediately if needed (only normal capsule)
        if send_email_now:
            send_capsule_email(recipient_email, text, [file.filename for file in uploaded_files])

        flash("Capsule created successfully!")
        return redirect('/my-capsules')

    return render_template('create.html')





@capsule.route('/my-capsules')
def my_capsules():
    if 'user' not in session:
        return redirect('/login')
    user_capsules = Capsule.query.filter_by(owner_username=session['user']).order_by(Capsule.created_at.desc()).all()
    return render_template('my_capsules.html', capsules=user_capsules)



@capsule.route('/capsule/<int:id>', methods=['GET', 'POST'])
def view_capsule(id):
    capsule_obj = Capsule.query.get_or_404(id)

    # Prevent early access

    if capsule_obj.delivery_date and capsule_obj.delivery_date > date.today():
        return f"⏳ This capsule will be viewable on {capsule_obj.delivery_date.strftime('%Y-%m-%d')}.", 403


    # Encrypted Capsules
    if capsule_obj.type == 'encrypted':
        if request.method == 'POST':
            entered_password = request.form['password']
            if entered_password == capsule_obj.encryption:
                files = File.query.filter_by(capsule_id=id).all()
                return render_template('view_capsule.html', capsule=capsule_obj, files=files)
            else:
                return render_template('encrypted_capsule.html', error="Incorrect password")
        return render_template('encrypted_capsule.html', error=None)

    # Public or Owner Private
    if capsule_obj.accessibility == 'public' or (
        capsule_obj.accessibility == 'private' and capsule_obj.owner_username == session.get('user')
    ):
        files = File.query.filter_by(capsule_id=id).all()
        return render_template('view_capsule.html', capsule=capsule_obj, files=files)

    return "You are not authorized to view this capsule.", 403


@capsule.route('/capsule/delete/<int:id>', methods=['POST'])
def delete_capsule(id):
    if 'user' not in session:
        return redirect('/login')

    capsule_obj = Capsule.query.get_or_404(id)

    # Make sure user is authorized to delete
    if capsule_obj.owner_username != session['user']:
        return "Unauthorized", 403

    # Delete associated files first
    File.query.filter_by(capsule_id=id).delete()

    # Delete the capsule itself
    db.session.delete(capsule_obj)
    db.session.commit()

    flash("Capsule deleted successfully.")
    return redirect('/my-capsules')

@capsule.route('/search')
def search_capsules():
    query = request.args.get('query', '')
    
    capsules = Capsule.query.filter(
        Capsule.accessibility == 'public'
    )

    if query:
        capsules = capsules.filter(
            (Capsule.owner_username.ilike(f"%{query}%")) | 
            (Capsule.title.ilike(f"%{query}%")) |
            (Capsule.tags.ilike(f"%{query}%")) |
            (db.cast(Capsule.created_at, db.String).ilike(f"%{query}%"))
        )
    sort = request.args.get('sort', 'newest')

    if sort == 'oldest':
        capsules = capsules.order_by(Capsule.created_at.asc())
    else:
        capsules = capsules.order_by(Capsule.created_at.desc())

    capsules = capsules.order_by(Capsule.created_at.desc()).all()
    return render_template('home.html', capsules=capsules)


import zipfile
import io
import json
from flask import send_file, current_app, abort

@capsule.route('/capsule/download/<int:id>')
def download_capsule(id):
    capsule_obj = Capsule.query.get_or_404(id)

    # Only allow the owner to download
    if capsule_obj.owner_username != session.get('user'):
        return "Unauthorized", 403

    # Start a zip buffer
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add capsule content to a text file
        content = f"""PastPort Capsule #{capsule_obj.id}
--------------------------------------
Message: {capsule_obj.text}
Type: {capsule_obj.type}
Delivery Date: {capsule_obj.delivery_date}
Tags: {capsule_obj.tags or '-'}
Encrypted: {capsule_obj.encryption != 'N/A'}
Status: {"Sent" if capsule_obj.sent else "Not Sent"}
"""
        zipf.writestr('capsule.txt', content)

        # Add uploaded files (if any)
        files = File.query.filter_by(capsule_id=id).all()
        for file in files:
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', file.filename)
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=file.filename)
            else:
                print(f" File not found: {file_path}")

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=f"capsule_{capsule_obj.id}.zip",
        mimetype='application/zip'
    )



def deliver_memorial_capsule(capsule):
    subject = "A Final Message From Your Loved One"
    body = f"This is the final message from {capsule.title}:\n\n{capsule.content}"
    for recipient_email in capsule.recipient_emails:
        send_email(recipient_email, subject, body)


def get_capsule_owner_email(capsule_id):
    capsule = Capsule.query.get(capsule_id)
    if capsule:
        user = User.query.filter_by(username=capsule.owner_username).first()
        if user:
            return user.email
    return None


@capsule.route('/verify/<token>')
def verify_death(token):
    data = decode_verifier_token(token)
    if not data:
        return "❌ Invalid or expired link.", 400
    
    capsule = Capsule.query.get(data['capsule_id'])
    if not capsule:
        return "❌ Capsule not found.", 404

    verifier_email = data['verifier_email']

    if verifier_email not in capsule.verifier_emails:
        return "❌ You are not authorized to verify.", 403

    # Ensure verifier_confirmations is a list, not None
    if not capsule.verifier_confirmations:
        capsule.verifier_confirmations = []

    # Check if the verifier has already confirmed
    if verifier_email in capsule.verifier_confirmations:
        return "✅ Already confirmed.", 200

    # Add verifier email to confirmations
    capsule.verifier_confirmations.append(verifier_email)
    
    # Commit immediately after the update to save to the database
    db.session.commit()

    # Explicitly refresh the capsule object to ensure the latest data is fetched
    db.session.refresh(capsule)  # Refresh the capsule object to reload from the database

    # Send email to capsule owner
    capsule_owner_email = get_capsule_owner_email(capsule.id)
    if capsule_owner_email:
        subject = "🔔 A Verifier Has Confirmed"
        body = f"Verifier {verifier_email} has confirmed the death for capsule {capsule.id}."
        send_email(capsule_owner_email, subject, body)

    # If enough confirmations (example: 2 needed), deliver the capsule
    if len(capsule.verifier_confirmations) >= 2:
        deliver_memorial_capsule(capsule)

    return "✅ Thank you! You have successfully confirmed."



# Like a capsule
@capsule.route('/capsule/like/<int:id>', methods=['POST'])
def like_capsule(id):
    if 'user' not in session:
        flash("You must be logged in to like a capsule.")
        return redirect(url_for('auth.login'))

    capsule = Capsule.query.get_or_404(id)
    user = session['user']

    # Only allow liking for public capsules
    if capsule.accessibility != 'public':
        flash("You can only like public capsules.")
        return redirect(request.referrer or url_for('capsule.view_capsule', id=id))

    # Check if the user has already liked this capsule
    existing_like = Like.query.filter_by(capsule_id=id, user_id=user).first()
    if existing_like:
        flash("You have already liked this capsule.")
    else:
        new_like = Like(capsule_id=id, user_id=user)
        db.session.add(new_like)

        # Create a notification for the capsule owner
        owner_username = capsule.owner_username
        if owner_username != user:  # Do not notify the user if they liked their own capsule
            notification = Notification(
                user_id=owner_username,
                capsule_id=id,
                message=f"{user} liked your capsule '{capsule.title}'"
            )
            db.session.add(notification)

        db.session.commit()
        flash("You liked this capsule.")

    return redirect(request.referrer or url_for('capsule.view_capsule', id=id))


# Unlike a capsule
@capsule.route('/capsule/unlike/<int:id>', methods=['POST'])
def unlike_capsule(id):
    if 'user' not in session:
        flash("You must be logged in to unlike a capsule.")
        return redirect(url_for('auth.login'))

    capsule = Capsule.query.get_or_404(id)
    user = session['user']

    # Check if the user has liked this capsule
    like = Like.query.filter_by(capsule_id=id, user_id=user).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        flash("You unliked this capsule.")
    else:
        flash("You haven't liked this capsule yet.")

    return redirect(request.referrer or url_for('capsule.view_capsule', id=id))
