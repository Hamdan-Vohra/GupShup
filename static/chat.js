let socket = io("http://localhost:5000", {
  transports: ["websocket", "polling"],
});
let currentUser = "";

function register(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const phone = document.getElementById("phone_number").value;
  const password = document.getElementById("password").value;
  const confirm_password = document.getElementById("password-confirm").value;

  print(JSON.stringify({ username, phone, password, confirm_password }));
  fetch("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, phone, password, confirm_password }),
  })
    .then((res) => res.json())
    .then((data) => {
      alert(
        data.success ? "Registered!" : data.message || "Registration failed."
      );
    })
    .catch((err) => {
      console.error("Error:", err);
      alert("Something went wrong.");
    });
}

function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        currentUser = username;
        // document.getElementById("currentUser").innerText = username;
        // document.getElementById("chat-ui").style.display = "block";
        socket.emit("connect_user", { username });
      } else {
        alert("Invalid credentials");
      }
    });
}

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
