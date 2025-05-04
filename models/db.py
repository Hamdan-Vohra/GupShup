from pymongo import MongoClient, errors
from werkzeug.security import generate_password_hash, check_password_hash
from config import MONGO_URI
from pymongo import ASCENDING

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("Successfully connected to MongoDB Atlas!")
except errors.ServerSelectionTimeoutError as err:
    print("Could not connect to MongoDB:", err)
    exit(1) 

db = client["chat_app"]

# GETTING username or phone_number
def find_user(user):
    return db.users.find_one({
    "$or": [
        {"username": user},
        {"phone": user}
    ]
    })

def register_user(username, phonenumber, password):
    try:
        # Verification If User Already Exits
        if db.users.find_one({"username": username}):
            return {"success": False, "message": "Username already exists"}

        if db.users.find_one({"phone": phonenumber}):
            return {"success": False, "message": "Phone number already registered"}


        hashed_pw = generate_password_hash(password)
        db.users.insert_one({
            "username": username,
            "password": hashed_pw,
            "phone": phonenumber,
            "friends": [] 
        })

        return {"success": True, "message": "User registered successfully"}

    except errors.PyMongoError as e:
        print("Database error during registration:", e)
        return {"success": False, "message": "An error occurred while registering the user"}


def authenticate_user(username, password):
    password = password.strip()
    username = username.strip()
    user = find_user(username)
    if not user:
        return {"success": False, "message": "User not found","user":None}
    
    if check_password_hash(user["password"], password):
        return {"success":True,"message":f"{user["username"]} LoggedIn Successfully","user":user}
    
    return {"success":False,"message":"Password is Incorrect!","user":None}

def db_add_friend(user1, user2):
    if user1 == user2:
        return {"success":False,"message":"Both users are same"}
    user = find_user(user1)
    friend = find_user(user2)
    if not friend or not user:
        return {"success":False,"message":"Friend not exist"}
    elif  are_friends(user['phone'],friend['phone']):
        return {"success":False,"message":" Already friends"}
    db.users.update_one({"username": user1}, {"$addToSet": {"friends": friend["phone"]}})
    # db.users.update_one({"phone": user2}, {"$addToSet": {"friends": user["phone"]}})
    return {"success":True,"message":f"{user['username']} has a new friend:  {friend['username']}"}


def are_friends(user1, user2):
    user = find_user(user1)
    friend = find_user(user2)
    return user and friend["phone"] in user.get("friends", [])

def friends_list(username):
    user = db.users.find_one({'username': username})
    if not user:
        return {"success":False,"friends":None}
    friend_ids = user.get('friends', [])
    friends = db.users.find({'phone': {'$in': [phone_number for phone_number in friend_ids]}})
    return {"success":True,"friends":friends}

def store_message(sender, receiver, content,timestamp):
    db.messages.insert_one({"from": sender, "to": receiver, "content": content,"timestamp":timestamp})
    if not are_friends(receiver,sender):
        db_add_friend(receiver,sender)

def get_chat_history(user1, user2):
    print(user1,user2)
    return list(db.messages.find({
            "$or": [
                {"from": user1, "to": user2},
                {"from": user2, "to": user1}
            ]
        }).sort("timestamp", 1))
