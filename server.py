import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

users = {}          
friends = {}       
online_users = {}  

def handle_client(client):
    username = None
    try:
        username = authenticate_user(client)
        if not username:
            client.close()
            return

        online_users[username] = client
        send(client, f"Welcome {username}! Use /addfriend <username> to add friends. /msg <friend> <message> to chat.")
        while True:
            msg = client.recv(1024).decode()
            if msg.startswith("/addfriend "):
                add_friend(username, msg[11:], client)
            elif msg.startswith("/msg "):
                parts = msg[5:].split(" ", 1)
                if len(parts) == 2:
                    send_message(username, parts[0], parts[1])
            else:
                send(client, "Unknown command.")
    except:
        pass
    finally:
        if username in online_users:
            del online_users[username]
        client.close()

def authenticate_user(client):
    send(client, "Do you want to [login] or [register]?")
    choice = client.recv(1024).decode()
    send(client, "Enter username:")
    username = client.recv(1024).decode()
    send(client, "Enter password:")
    password = client.recv(1024).decode()

    if choice == "register":
        if username in users:
            send(client, "Username already exists.")
            return None
        users[username] = password
        friends[username] = set()
        send(client, "Registration successful.")
    elif choice == "login":
        if users.get(username) != password:
            send(client, "Invalid credentials.")
            return None
        send(client, "Login successful.")
    else:
        send(client, "Invalid choice.")
        return None
    return username

def add_friend(username, friend, client):
    if friend not in users:
        send(client, "User not found.")
        return
    friends[username].add(friend)
    friends[friend].add(username)
    send(client, f"You are now friends with {friend}")

def send_message(sender, recipient, message):
    if recipient not in friends.get(sender, set()):
        send(online_users[sender], "You are not friends with this user.")
        return
    if recipient not in online_users:
        send(online_users[sender], "User is not online.")
        return
    send(online_users[recipient], f"{sender}: {message}")

def send(client, msg):
    client.send((msg + "\n").encode())

print(f"Server running on {HOST}:{PORT}")
while True:
    client, addr = server.accept()
    threading.Thread(target=handle_client, args=(client,)).start()
