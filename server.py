import socket
import threading

# List to hold client connections
clients = []
nicknames = []

# Create TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 12345))  # Bind to public IP and port
server.listen()

print("Server running and waiting for connections...")

def broadcast(message, client):
    """Send message to all clients except the sender."""
    for c in clients:
        if c != client:
            try:
                c.send(message)
            except:
                clients.remove(c)

def handle_client(client):
    """Handle messages from a client."""
    while True:
        try:
            msg = client.recv(1024)
            broadcast(msg, client)
        except:
            # Remove client when disconnected
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f"{nickname} left the chat!".encode(), client)
            break

def receive():
    """Accept new clients continuously."""
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send("NICK".encode())
        nickname = client.recv(1024).decode()
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode(), client)
        client.send("Connected to the server!".encode())

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

receive()

