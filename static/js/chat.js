let socket = io("http://localhost:5000", {
  transports: ["websocket", "polling"],
});

function addFriend() {
  const friend = document.getElementById("friend").value;
  fetch("/add_friend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: currentUser, friend }),
  })
    .then((res) => res.json())
    .then((data) =>
      alert(data.success ? "Friend added!" : "Could not add friend.")
    );
}

function sendMessage() {
  const to = document.getElementById("recipient").value;
  const message = document.getElementById("message").value;
  socket.emit("send_message", {
    from: currentUser,
    to: to,
    message: message,
  });
  addMessage(`You → ${to}: ${message}`);
}

function addMessage(msg) {
  const container = document.getElementById("messages");
  const p = document.createElement("p");
  p.innerText = msg;
  container.appendChild(p);
  container.scrollTop = container.scrollHeight;
}

socket.on("receive_message", (data) => {
  addMessage(`${data.from} → You: ${data.message}`);
});

socket.on("error", (data) => {
  alert(data.message);
});
