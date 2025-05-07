from flask import Blueprint, render_template, request, jsonify, session
from flask_socketio import emit, join_room
import qrcode
import io
import base64
import yagmail
from models import db, CollaborativeMessage  # Import the new model
from flask import session

# Create Blueprint
collab = Blueprint('collab', __name__, url_prefix='/collab')

# Email setup
SENDER_EMAIL = "rajesh.saha.shawon@g.bracu.ac.bd"
APP_PASSWORD = 'akkq pfcu aenc wtmq'
yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)

# In-memory store: room_id -> { message, users, history }
collab_rooms = {}

@collab.route('/')
def collab_ui():
    return render_template('collab.html')

@collab.route('/create-room', methods=['POST'])
def create_room():
    room_id = request.json.get('room_id')
    if not room_id or not room_id.isdigit() or len(room_id) != 8:
        return jsonify({'error': 'Room ID must be an 8-digit number'}), 400
    if room_id in collab_rooms:
        return jsonify({'error': 'Room already exists'}), 400
    collab_rooms[room_id] = {'message': '', 'users': set(), 'history': []}
    return jsonify({'room_id': room_id}), 200

@collab.route('/send-invite', methods=['POST'])
def send_invite():
    data = request.json
    email = data.get('email')
    room_id = data.get('room_id')
    if not email or not room_id:
        return jsonify({'error': 'Missing email or room ID'}), 400

    invite_link = f"https://pastport-six.vercel.app/collab"
    try:
        qr = qrcode.make(invite_link)
        buffered = io.BytesIO()
        qr.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        qr_img_html = f'<img src="data:image/png;base64,{qr_base64}" alt="QR Code" style="width:200px;height:200px;">'

        html_content = f"""
        <html>
          <body style="font-family:Arial,sans-serif;">
            <h2>📝 Join My Collaborative Message Room</h2>
            <p>Hello! You've been invited to collaborate in a message room.</p>
            <p><strong>Room ID:</strong> {room_id}</p>
            <p>Use the Room ID to join or scan the QR code below:</p>
            {qr_img_html}
            <p>Or click the link to join directly:</p>
            <p><a href="{invite_link}" style="color:#4facfe;">{invite_link}</a></p>
            <p>Happy collaborating! 🚀</p>
          </body>
        </html>
        """
        yag.send(to=email, subject="🧠 You're Invited to Collaborate", contents=html_content)
        return jsonify({'success': True, 'message': f'Invitation sent to {email}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Socket.IO Events

def register_socketio_handlers(socketio):
    @socketio.on('join')
    def on_join(data):
        # Retrieve username from session
        username = session.get('user')  # Assume the username is stored in the session
        room_id = data['room_id']

        if not username:
            return jsonify({'error': 'User must be logged in to join the room'}), 400

        join_room(room_id)

        if room_id not in collab_rooms:
            collab_rooms[room_id] = {'message': '', 'users': set(), 'history': []}

        collab_rooms[room_id]['users'].add(username)

        emit('user_joined', {
            'username': username,
            'message': collab_rooms[room_id]['message'],
            'users': list(collab_rooms[room_id]['users']),
            'history': collab_rooms[room_id]['history']
        }, room=room_id)

    @socketio.on('update_message')
    def on_update(data):
        room_id = data['room_id']
        new_message = data['message']
        
        # Retrieve username from session
        username = session.get('user')  # Assume the username is stored in the session

        if not username:
            return jsonify({'error': 'User must be logged in to update the message'}), 400

        # Save message to the database
        new_message_entry = CollaborativeMessage(
            room_id=room_id,
            username=username,
            message=new_message
        )
        db.session.add(new_message_entry)
        db.session.commit()

        # Update the in-memory store as well (optional)
        collab_rooms[room_id]['message'] = new_message
        collab_rooms[room_id]['history'].append(new_message)

        emit('message_updated', {
            'message': new_message,
            'history': collab_rooms[room_id]['history']
        }, room=room_id)


@collab.route('/send-message-email', methods=['POST'])
def send_message_email():
    data = request.json
    email = data.get('email')
    room_id = data.get('room_id')
    message = data.get('message')

    if not email or not room_id or not message:
        return jsonify({'error': 'Missing email, room ID, or message'}), 400

    # Fetch the message and other details if necessary
    try:
        subject = f"Collaborative Message from Room {room_id}"
        body = f"Message from Room {room_id}:\n\n{message}"

        yag.send(to=email, subject=subject, contents=body)
        return jsonify({'success': True, 'message': 'Message sent via email'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
