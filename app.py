from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from config import SECRET_KEY
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room

from flask_cors import CORS


from frontend.routes import frontend_routes

from models.db import (
    register_user, authenticate_user,
    add_friend, are_friends,
    store_message, get_chat_history
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
        flash('All fields must be filled.', 'danger')
    elif len(password) < 8:
        flash('Passwords Length Must be 8 or greater.', 'warning')
    else:
        res = authenticate_user(username, password)
        if res["success"]:
            session['username'] = username
            flash(res['message'], 'success')
            return redirect(url_for("frontend_routes.ChatApp"))
        else:
            flash(res['message'], 'danger')
    return redirect(url_for("login"))


        
@app.route("/add_friend", methods=["POST"])
def add_friend():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"})
    user = session['username']
    friends_number = request.form.get("friends-number")
    result = add_friend(user, friends_number)
    return jsonify({"success": result})


@socketio.on("connect_user")
def connect_user(data):
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
    for user, sid in list(online_users.items()):
        if sid == request.sid:
            del online_users[user]
            break

if __name__ == "__main__":
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet") 
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
