const currentUser = window.currentUser || "Guest";
let selectedFriend = null;
const friendListContainer = document.getElementById("friend-list");
const chatInput = document.getElementById("chat-input");

let socket = io("http://localhost:5000", {
  auth: { username: currentUser },
});

socket.on("connect", () => {
  console.log("Connected to server. Socket ID:", socket.id);
  socket.emit("join", { username: currentUser });
});

socket.on("receive_message", (data) => {
  if (data.sender === selectedFriend) {
    appendMessage(data.sender, data.message, data.timestamp);
  } else {
  }
});

socket.on("friend_added", (data) => {
  const friendList = document.getElementById("friend-list");
  const newFriend = data.username;

  const exists = [...friendList.children].some(
    (li) => li.innerText.trim() === newFriend
  );

  if (!exists) {
    const li = document.createElement("li");
    li.innerHTML = `<button onclick="selectFriend('${newFriend}')" class="w-full text-left px-3 py-2 bg-white rounded shadow hover:bg-indigo-100">${newFriend}</button>`;
    friendList.appendChild(li);

    if (window.friendListData) {
      window.friendListData.push({ username: newFriend });
    }
  }
});

socket.on("error", (data) => {
  console.error("SocketIO error received:", data.message);
  alert(`Error: ${data.message}`);
});
// Socket Functionalities Ended

// Simple Javascript functions
// Load friend list on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  loadFriendList();
});

// Load friend list function
function loadFriendList() {
  friendListContainer.innerHTML = "";
  if (
    Array.isArray(window.friendListData) &&
    window.friendListData.length > 0
  ) {
    window.friendListData.forEach((friend) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <button onclick="selectFriend('${friend.username}')"
          class="w-full text-left px-3 py-2 bg-white rounded shadow hover:bg-indigo-100">
          ${friend.username}
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

// Select friend & load previous conversation
function selectFriend(friendUsername) {
  if (selectedFriend === friendUsername) {
    return;
  }
  const chatWith = document.getElementById("chat-with");
  const chatBox = document.getElementById("chat-box");
  const friendProfile = document.getElementById("friend-profile");

  selectedFriend = friendUsername;
  console.log("Selected friend:", selectedFriend);

  chatWith.textContent = friendUsername;
  friendProfile.classList.toggle("hidden");
  chatBox.innerHTML = "";

  fetch(`/get_messages/${friendUsername}`)
    .then((response) => response.json())
    .then((messages) => {
      messages.forEach((msg) => {
        appendMessage(msg.sender, msg.message, msg.timestamp);
      });
    })
    .catch((err) => console.error("Error fetching messages:", err));
}

// Append message to chat box
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
        : "bg-gray-200 text-black"
    }">
      <div>${message}</div>
      <div class="text-xs text-gray-500 mt-1">${time}</div>
    </div>`;

  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Send message function
function sendMessage() {
  const message = chatInput.value.trim();
  const timestamp = new Date().toISOString();

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

// Logout function
function LogOut() {
  fetch(`/logout`)
    .then((response) => response.json())
    .catch((err) => console.error("Error While Logout:", err));
}
