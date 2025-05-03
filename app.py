from flask import Flask, request, jsonify, render_template
from config import SECRET_KEY
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room
from flask import render_template, redirect, url_for, flash

from frontend.routes import frontend_routes

from models.db import (
    register_user, authenticate_user,
    add_friend, are_friends,
    store_message, get_chat_history
)

app = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="templates")
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*")

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
    elif password != confirm_password:
        flash('Passwords do not match.', 'danger')
    else:
        flash(f'Registration successful for {username}!', 'success')
        return redirect(url_for('login'))


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    success = authenticate_user(data["username"], data["password"])
    return jsonify({"success": success})

@app.route("/add_friend", methods=["POST"])
def add_friend_route():
    data = request.json
    result = add_friend(data["username"], data["friend"])
    return jsonify({"success": result})

@socketio.on("connect_user")
def handle_connect_user(data):
    username = data["username"]
    online_users[username] = request.sid
    emit("user_connected", {"message": f"{username} connected."}, broadcast=True)

@socketio.on("send_message")
def handle_send_message(data):
    sender = data["from"]
    recipient = data["to"]
    message = data["message"]
    if are_friends(sender, recipient):
        store_message(sender, recipient, message)
        sid = online_users.get(recipient)
        if sid:
            emit("receive_message", {"from": sender, "message": message}, room=sid)
    else:
        emit("error", {"message": "You are not friends with this user."}, room=request.sid)

@socketio.on("disconnect")
def handle_disconnect():
    for user, sid in online_users.items():
        if sid == request.sid:
            del online_users[user]
            break

if __name__ == "__main__":
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet") 
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)

