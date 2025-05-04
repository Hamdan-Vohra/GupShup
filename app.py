from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from config import SECRET_KEY
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
from flask_cors import CORS


from frontend.routes import frontend_routes

from models.db import (
    register_user, authenticate_user,
    db_add_friend, are_friends,
    store_message, get_chat_history,friends_list
)

app = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="templates")
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

online_users = {}  

app.register_blueprint(frontend_routes)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    confirm_password = request.form.get('password-confirm')

    if not all([username, phone_number, password, confirm_password]):
        flash('All fields are required.', 'danger')
    elif len(password) < 8:
        flash('Passwords Length Doesn\'t Match.', 'warning')
    elif password != confirm_password:
        flash('Passwords do not match.', 'danger')
    else:
        response = register_user(username=username,password=password,phonenumber=phone_number)
        if response["success"]:
            flash(response["message"], 'success')
            return redirect(url_for('login'))
        else:
            flash(response["message"], 'danger')
    return redirect(url_for('register'))



@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        session.pop('_flashes', None)
        flash('All fields must be filled.', 'danger')
    elif len(password) < 8:
        session.pop('_flashes', None)
        flash('Passwords Length Must be 8 or greater.', 'warning')
    else:
        res = authenticate_user(username, password)
        if res["success"]:
            user = res["user"]
            session['username'] = user["username"]
            session.pop('_flashes', None)
            flash(res['message'], 'success')
            return redirect(url_for("chat"))
        else:
            session.pop('_flashes', None)
            flash(res['message'], 'danger')
    return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    username = session['username']
    print("/chat",username)
    if 'username' not in session:
        return redirect(url_for('login'))
    res = friends_list(username)
    if res["success"]:
        return render_template('chat-app.html', username=username, friends=res["friends"])
    return redirect(url_for('login'))

        
@app.route("/add_friend", methods=["POST"])
def add_friend():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"})
    user = session['username']
    friends_number = request.form.get("friend_phone")
    print(friends_number)
    res = db_add_friend(user, friends_number)
    if res["success"]:
        session.pop('_flashes', None)
        flash(res["message"],'success')
    else:
        session.pop('_flashes', None)
        flash(res["message"],'error')  
    print(res)
    return redirect(url_for("chat"))

@socketio.on('join')
def handle_join(data):
    username = data.get("username")
    online_users[username] = request.sid
    print(f"{username} joined with SID {request.sid}")

@socketio.on('send_message')
def handle_send_message(data):
    sender = [k for k, v in online_users.items() if v == request.sid]
    sender_username = sender[0] if sender else "Unknown"

    recipient = data['recipient']
    message = data['message']
    timestamp = data['timestamp']

    print(f"[{timestamp}] {sender_username} ➜ {recipient}: {message}")

    if are_friends(sender_username, recipient):
        store_message(sender_username, recipient, message,timestamp)
    else:
        emit("error", {"message": "You are not friends with this user."}, room=request.sid)

    if recipient in online_users:
        emit('receive_message', {
            'sender': sender_username,
            'message': message,
            'timestamp': timestamp
        }, room=online_users[recipient])
    else:
        print(f"Recipient {recipient} not connected.")
        emit("error", {"message": f"Recipient {recipient} not connected."}, room=request.sid)


@app.route("/get_messages/<friend>")
def get_messages(friend):
    if "username" not in session:
        return redirect(url_for("login"))

    current_user = session["username"]
    messages = get_chat_history(current_user, friend)
    print(messages)
    # Filtering Messages
    messages_filtered = [
        {
            "sender": m["from"],
            "message": m["content"],
            "timestamp": m.get("timestamp"),
            "isOwnMessage": m["from"] == current_user
        } for m in messages
    ]
    return jsonify(messages_filtered)

@socketio.on('disconnect')
def handle_disconnect(*args):
    print("Client disconnected")
    for user, sid in list(online_users.items()):
        if sid == request.sid:
            del online_users[user]
            break

@socketio.on_error() 
def error_handler(e):
    print('SocketIO Error:', e)

@socketio.on_error_default 
def default_error_handler(e):
    print('Default error handler:', e)

if __name__ == "__main__":
    # socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet") 
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
