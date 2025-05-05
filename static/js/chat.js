let socket = io("http://localhost:5000");

let selectedFriend = "";

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
function selectFriend(friendUsername) {
  selectedFriend = friendUsername;
  document.getElementById("chat-with").textContent = friendUsername;
  document.getElementById("chat-box").innerHTML = "";
  fetch(`/get_messages/${friendUsername}`)
    .then((response) => response.json())
    .then((messages) => {
      messages.forEach((msg) => {
        appendMessage(msg.sender, msg.message, msg.timestamp);
      });
    })
    .catch((err) => console.error("Error fetching messages:", err));
}

function loadFriendList() {
  const friendList = document.getElementById("friend-list");
  friendList.innerHTML = "";
  console.log("Friends:", window.friendListData);

  if (
    Array.isArray(window.friendListData) &&
    window.friendListData.length > 0
  ) {
    window.friendListData.forEach((friend) => {
      const li = document.createElement("li");
      li.innerHTML = `<button onclick="selectFriend('${friend.username}')" class="w-full text-left px-3 py-2 bg-white rounded shadow hover:bg-indigo-100">${friend.username}</button>`;
      friendList.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.className = "text-gray-500 text-sm px-3 py-2";
    li.textContent = "No Friends yet!";
    friendList.appendChild(li);
  }
}

document.addEventListener("DOMContentLoaded", loadFriendList);

function appendMessage(sender, message, timestamp = null) {
  const chatBox = document.getElementById("chat-box");
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
    </div>
  `;

  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  const timestamp = new Date().toISOString();

  if (!message || !selectedFriend) return;

  socket.emit("send_message", {
    recipient: selectedFriend,
    message: message,
    timestamp: timestamp,
  });

  appendMessage(currentUser, message, timestamp);
  input.value = "";
}
