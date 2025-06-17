// chatStore.js
class User {
  constructor({ name, email, phone }) {
    if (!name || !email || !phone) {
      throw new Error("User fields are required");
    }
    this.name = name;
    this.email = email;
    this.phone = phone;
  }
}

class Friend {
  constructor({ name, lastMessage = "", messageType = "text" }) {
    if (!name) throw new Error("Friend must have a name");
    this.name = name;
    this.lastMessage = lastMessage;
    this.messageType = messageType; // 'text', 'image', etc.
  }
}

class Message {
  constructor({ sender, receiver, content, timestamp = Date.now() }) {
    if (!sender || !receiver || !content) {
      throw new Error("Message must have sender, receiver, and content");
    }
    this.sender = sender;
    this.receiver = receiver;
    this.content = content;
    this.timestamp = new Date(timestamp);
  }
}

class ChatStore {
  constructor() {
    this.currentUser = null;
    this.friends = [];
    this.messages = {};
    this.selectedFriend = null;
  }

  setCurrentUser(userData) {
    this.currentUser = new User(userData);
  }

  getCurrentUser() {
    return this.currentUser;
  }

  setFriends(friendList) {
    this.friends = friendList.map((f) => new Friend(f));
  }

  getFriends() {
    return this.friends;
  }

  setSelectedFriend(friendName) {
    this.selectedFriend = friendName;
  }

  getSelectedFriend() {
    return this.selectedFriend;
  }

  addMessage(friendName, messageData) {
    const message = new Message(messageData);
    if (!this.messages[friendName]) this.messages[friendName] = [];
    this.messages[friendName].push(message);
  }

  getMessages(friendName) {
    return this.messages?.[friendName] || [];
  }
}

// Singleton instance
const chatStore = new ChatStore();
export default chatStore;
