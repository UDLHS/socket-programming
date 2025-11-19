# Socket Programming Chat App

This project demonstrates a basic multi-user chat application written entirely with Python sockets. It contains:

- **server.py**: a threaded TCP server that accepts multiple clients, tracks usernames, and broadcasts messages.
- **client1.py**: a simple console-based client (adapt the name if you rename the file).
  
Together they illustrate how to design a simple application-layer protocol on top of TCP by explicitly framing every message with a fixed-size header.

---

## Features

- **Username handshake:** registers each client with the server.
- **Live chat broadcast:** every message is relayed to all connected peers (except the sender, who renders locally).
- **Private chat:** users can send direct messages to specific peers.
- **Active user list:** (if implemented) server may provide a list of currently connected users.
- **Graceful shutdown:** triggered when special commands are sent or the window closes.

---

## Architecture Overview

### Client (`client1.py`)
- Connects to the server and prompts for a username.
- Sends USERNAME:<name> so the server can identify future messages.
- Reads from the server in a background loop and displays broadcast or private messages.
- Wraps outgoing messages using the same framing scheme and displays the sender’s own text instantly for responsiveness.

### Server (`server.py`)
- Listens on `0.0.0.0:5050`, accepting each client in its own thread.
- Stores client metadata (address, username) in a shared dictionary (likely guarded by a lock).
- On each message, decides whether to broadcast, send privately, or process a disconnect.
- (Can) periodically send an active user list so clients remain in sync.
- Manages group and private messages as per the protocol.

---

## Why the `HEADER` Constant Matters

TCP is a stream: it has no concept of message boundaries. Both client and server preface every payload with a fixed-length header (`HEADER = 64`). The header encodes the length of the upcoming message and is padded with spaces to fill 64 bytes.

Typical read logic:
1. Read exactly 64 bytes.
2. Convert the stripped value into an integer length.
3. Call `recv(length)` to obtain the full message body.

Without this, reads could split or merge messages unpredictably.

---

## Requirements

- Python 3.8+
- Network connectivity between machines running the server and clients

---

## Running the Project

1. **Start the server**  
   On the machine you want as the host (server):
   ```bash
   python server.py
   ```

2. **Start a client**  
   On each client machine, edit the `SERVER` variable in `client1.py` to match your server's public or LAN IP as needed.

   Then run:
   ```bash
   python client1.py
   ```
   Enter a username when prompted and start chatting!  
   Use the application interface to send messages to all users or private messages.

---

## Customization Tips

- Change `PORT` in both files to move the service to a different TCP port.
- Extend the protocol with more control messages (e.g., for private chats) using reserved prefixes.
- Improve UI/UX as needed (e.g., add a GUI, sound notifications, etc.).

---

## Troubleshooting

- **Cannot connect:** Ensure the server is running and reachable. Firewalls must allow inbound TCP on the chosen port.
- **User list not updating:** Both sides should agree on the protocol for sync messages and JSON payload formatting.
- **Random disconnects:** Check for errors/exceptions and ensure headers and message sizes match on both sides.

---

## License

This project is open for use and modification.

---

Feel free to contribute or suggest enhancements!
