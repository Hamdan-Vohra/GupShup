from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["chat_app"]

def register_user(username,phonenumber,password):
    if db.users.find_one({"username": username}):
        return False
    hashed_pw = generate_password_hash(password)
    db.users.insert_one({"username": username, "password": hashed_pw, "phone":phonenumber ,"friends": []})
    return True

def authenticate_user(username, password):
    user = db.users.find_one({"username": username}) | db.users.find_one({"phone": username})
    if user and check_password_hash(user['password'], password):
        return True
    return False

def add_friend(user1, user2):
    if user1 == user2 or not db.users.find_one({"username": user2}):
        return False
    db.users.update_one({"username": user1}, {"$addToSet": {"friends": user2}})
    db.users.update_one({"username": user2}, {"$addToSet": {"friends": user1}})
    return True

def are_friends(user1, user2):
    user = db.users.find_one({"username": user1})
    return user and user2 in user.get("friends", [])

def store_message(sender, receiver, content):
    db.messages.insert_one({"from": sender, "to": receiver, "content": content})

def get_chat_history(user1, user2):
    return list(db.messages.find({
        "$or": [
            {"from": user1, "to": user2},
            {"from": user2, "to": user1}
        ]
    }).sort("timestamp"))
