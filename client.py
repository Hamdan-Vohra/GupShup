import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode()
            if message:
                print(message.strip())
        except:
            print("Disconnected from server.")
            break

def send_messages():
    while True:
        try:
            msg = input()
            client.send(msg.encode())
        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()

send_messages()
