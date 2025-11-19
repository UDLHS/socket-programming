import socket
import threading

clients = {}  # username → connection socket mapping
lock = threading.Lock()  # for thread-safe access to clients dict


def broadcast_user_list():
    """Send the updated list of users to all clients."""
    users = ",".join(clients.keys())
    msg = f"USERS:{users}".encode()

    for conn in clients.values():
        try:
            conn.send(msg)
        except:
            pass


def handle_client(conn, addr):
    print(f"New connection: {addr}")

    username = None  # define here so we can access in finally block

    try:
        # First message from client = username
        username = conn.recv(1024).decode()
        if not username:
            conn.close()
            return

        # Add the client
        with lock:
            if username in clients:
                conn.send("Username already taken.".encode())
                conn.close()
                return

            clients[username] = conn

        print(f"{username} joined the chat.")
        broadcast_user_list()

        # FIX: Send connection success response only to this client
        # conn.send("SERVER:ConnectedSuccessfully".encode())

        # Notify others
        for user, client_conn in clients.items():
            if user != username:
                try:
                    client_conn.send(f"{username} joined the chat.".encode())
                except:
                    pass

        # Main receive loop
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            # Private message format: SEND_TO:receiver:message
            if data.startswith("SEND_TO:"):
                try:
                    _, receiver, message = data.split(":", 2)

                    with lock:
                        if receiver in clients:
                            clients[receiver].send(f"FROM:{username}:{message}".encode())

                        elif receiver.lower() == "everyone":
                            for user, client_conn in clients.items():
                                if user != username:
                                    client_conn.send(f"{username}: {message}".encode())

                        else:
                            conn.send("User not found.".encode())

                except ValueError:
                    conn.send("Invalid format. Use SEND_TO:receiver:message".encode())

            else:
                # Normal broadcast
                with lock:
                    for user, client_conn in clients.items():
                        if user != username:
                            try:
                                client_conn.send(f"{username}: {data}".encode())
                            except:
                                pass

    except Exception as e:
        print(f"Error with {username}: {e}")

    finally:
        # Cleanup on disconnect
        with lock:
            if username in clients:
                del clients[username]
                print(f"{username} disconnected.")
                broadcast_user_list()

        conn.close()


def start_server():
    host = "0.0.0.0"
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server started on {host}:{port}... Waiting for connections.")

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    start_server()
