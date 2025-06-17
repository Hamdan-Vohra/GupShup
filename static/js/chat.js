// chat.js
import chatStore from "./store";

chatStore.setSelectedFriend(null);
const currentUser = chatStore.getCurrentUser()?.name || "Guest";

// Elements
const friendListContainer = document.getElementById("friend-list");
const chatWith = document.getElementById("chat-with");
const chatBox = document.getElementById("chat-box");
const chatInput = document.getElementById("chat-input");

// Socket.IO Setup
let socket = io("http://localhost:5000", {
  auth: { username: currentUser },
});

socket.on("connect", () => {
  console.log("Connected to server. Socket ID:", socket.id);
  socket.emit("join", { username: currentUser });
});

socket.on("receive_message", (data) => {
  chatStore.addMessage(data.sender, data);
  if (data.sender === chatStore.getSelectedFriend()) {
    appendMessage(data.sender, data.message, data.timestamp);
  }
});

socket.on("friend_added", (data) => {
  const newFriend = data.username;
  if (!chatStore.getFriends().some((f) => f.name === newFriend)) {
    chatStore.setFriends([
      ...chatStore.getFriends(),
      { name: newFriend, lastMessage: "", messageType: "text" },
    ]);
    loadFriendList();
  }
});

socket.on("error", (data) => {
  console.error("SocketIO error received:", data.message);
  alert(`Error: ${data.message}`);
});

// DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  loadFriendList();
});

function loadFriendList() {
  friendListContainer.innerHTML = "";

  const friends = chatStore.getFriends();
  if (Array.isArray(friends) && friends.length > 0) {
    friends.forEach((friend) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <button onclick="selectFriend('${friend.name}')"
          class="w-full text-left px-3 py-2 bg-white dark:bg-gray-800 rounded shadow hover:bg-indigo-100 dark:hover:bg-indigo-900 text-black dark:text-white">
          ${friend.name}
        </button>`;
      friendListContainer.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.className = "text-gray-500 text-sm px-3 py-2";
    li.textContent = "No Friends yet!";
    friendListContainer.appendChild(li);
  }
}

function selectFriend(friendUsername) {
  chatStore.setSelectedFriend(friendUsername);
  chatWith.textContent = friendUsername;
  chatBox.innerHTML = "";

  fetch(`/get_messages/${friendUsername}`)
    .then((response) => response.json())
    .then((messages) => {
      messages.forEach((msg) => {
        chatStore.addMessage(friendUsername, msg);
        appendMessage(msg.sender, msg.message, msg.timestamp);
      });
    })
    .catch((err) => console.error("Error fetching messages:", err));
}

function appendMessage(sender, message, timestamp = null) {
  const msgDiv = document.createElement("div");
  const time = timestamp ? new Date(timestamp).toLocaleTimeString() : "";

  msgDiv.className = `mb-2 ${
    sender === currentUser ? "text-right" : "text-left"
  }`;

  msgDiv.innerHTML = `
    <div class="inline-block px-4 py-2 rounded-lg ${
      sender === currentUser
        ? "bg-purple-600 text-white"
        : "bg-gray-200 text-black dark:bg-gray-700 dark:text-white"
    }">
      <div>${message}</div>
      <div class="text-xs text-gray-500 mt-1">${time}</div>
    </div>`;

  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
  const message = chatInput.value.trim();
  const timestamp = new Date().toISOString();

  const selectedFriend = chatStore.getSelectedFriend();
  if (!message || !selectedFriend) {
    alert("Select a friend first & type message.");
    return;
  }

  socket.emit("send_message", {
    recipient: selectedFriend,
    message: message,
    timestamp: timestamp,
  });

  appendMessage(currentUser, message, timestamp);
  chatInput.value = "";
}

function LogOut() {
  fetch(`/logout`)
    .then((response) => response.json())
    .catch((err) => console.error("Error While Logout:", err));
}
