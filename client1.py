import customtkinter as ctk
import socket
import threading

# ============================================================== #
#                   CHAT CLIENT (Socket Logic)                  #
# ============================================================== #
class ChatClient:
    def __init__(self):
        self.client_socket = None
        self.username = None
        self.connected = False

    def connect_to_server(self):
        host = "16.171.62.113"  # "localhost"
        port = 5000
        try:
            self.client_socket = socket.socket()
            self.client_socket.connect((host, port))
            self.connected = True
            return True
        except:
            self.connected = False
            return False

    def send_message(self, msg):
        try:
            self.client_socket.send(msg.encode())
        except:
            pass

    def receive_messages(self, callback):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if data:
                    callback(data)
                else:
                    break
            except:
                break


# ============================================================== #
#                      CHAT GUI (UI)                             #
# ============================================================== #
class ChatGUI:
    def __init__(self):
        self.client = ChatClient()
        self.target_user = "everyone"
        self.chat_history = {"everyone": []}

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.app = ctk.CTk()
        self.app.title("Private Chat App")
        self.app.geometry("700x600")

        # ------------------------------- #
        # Main layout                     #
        # ------------------------------- #
        main_frame = ctk.CTkFrame(self.app)
        main_frame.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkFrame(main_frame, width=150)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="Online Users").pack(pady=10)

        self.user_buttons = []

        self.group_btn = ctk.CTkButton(
            self.sidebar, text="Group Chat",
            width=120, command=lambda: self.select_user("everyone")
        )
        self.group_btn.pack(pady=5)
        self.user_buttons.append(self.group_btn)

        # ------------------------------- #
        # Message bubble chat area        #
        # ------------------------------- #
        self.chat_frame = ctk.CTkScrollableFrame(main_frame, width=480, height=460)
        self.chat_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ------------------------------- #
        # Message input                   #
        # ------------------------------- #
        input_frame = ctk.CTkFrame(self.app)
        input_frame.pack(fill="x", pady=8)

        self.message_entry = ctk.CTkEntry(
            input_frame, width=500, height=40,
            placeholder_text="Type your message..."
        )
        self.message_entry.pack(side="left", padx=10)

        self.send_button = ctk.CTkButton(
            input_frame, text="Send", width=120, height=40,
            command=self.send_clicked
        )
        self.send_button.pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(self.app, text="Not connected")
        self.status_label.pack(pady=5)

        self.reconnect_button = ctk.CTkButton(
            self.app, text="Reconnect", width=200,
            command=self.reconnect
        )
        self.reconnect_button.pack(pady=5)

        self.start_connection()
        self.app.mainloop()

    # ============================================================== #
    #                       CONNECTION                               #
    # ============================================================== #
    def start_connection(self):
        success = self.client.connect_to_server()

        if success:
            self.status_label.configure(text="Connected ✔", text_color="lightgreen")
            self.ask_username()

            threading.Thread(
                target=self.client.receive_messages,
                args=(self.handle_server_message,),
                daemon=True
            ).start()
        else:
            self.status_label.configure(text="❌ Connection failed", text_color="red")
            self.add_bubble("⚠️ Could not connect to server.", "left")

    def reconnect(self):
        self.status_label.configure(text="Reconnecting...", text_color="yellow")
        self.add_bubble("⏳ Trying to reconnect...", "left")

        try:
            if self.client.client_socket:
                self.client.client_socket.close()
        except:
            pass

        success = self.client.connect_to_server()

        if success:
            self.status_label.configure(text="Reconnected ✔", text_color="lightgreen")

            if self.client.username:
                self.client.send_message(self.client.username)

            threading.Thread(
                target=self.client.receive_messages,
                args=(self.handle_server_message,),
                daemon=True
            ).start()
        else:
            self.status_label.configure(text="Reconnect failed ❌", text_color="red")
            self.add_bubble("⚠️ Could not reconnect.", "left")

    # ============================================================== #
    #                MESSAGE BUBBLES (LEFT/RIGHT)                   #
    # ============================================================== #
    def add_bubble(self, text, side):
        """Creates a chat bubble aligned left or right."""
        bubble = ctk.CTkLabel(
            self.chat_frame,
            text=text,
            fg_color="#1f6aa5" if side == "right" else "#444444",
            text_color="white",
            corner_radius=12,
            wraplength=300,
            padx=12,
            pady=8
        )
        bubble.pack(
            anchor="e" if side == "right" else "w",
            pady=3,
            padx=8
        )

    # ============================================================== #
    #                   HANDLE SERVER MESSAGES                       #
    # ============================================================== #
    def handle_server_message(self, message):
        if message.startswith("USERS:"):
            users = message.replace("USERS:", "").split(",")
            self.update_user_list(users)
            return

        if message.startswith("FROM:"):
            _, sender, msg = message.split(":", 2)
            target = sender
            self.show_message(f"{sender}: {msg}", target, sender="other")
            return

        self.show_message(message, "everyone", sender="other")

    # ============================================================== #
    #                UPDATE USER LIST IN SIDEBAR                     #
    # ============================================================== #
    # def update_user_list(self, users):
    #     for btn in self.user_buttons[1:]:
    #         btn.destroy()
    #     self.user_buttons = self.user_buttons[:1]
    #
    #     for user in users:
    #         btn = ctk.CTkButton(
    #             self.sidebar, text=user,
    #             width=120,
    #             command=lambda u=user: self.select_user(u)
    #         )
    #         btn.pack(pady=5)
    #         self.user_buttons.append(btn)

    def update_user_list(self, users):
        # Remove old buttons safely (DON’T DESTROY)
        for btn in self.user_buttons[1:]:
            btn.pack_forget()

        # Keep only group button
        self.user_buttons = self.user_buttons[:1]

        # Add new user buttons
        for user in users:
            if user == self.client.username:
                continue  # don't add yourself to sidebar

            btn = ctk.CTkButton(
                self.sidebar,
                text=user,
                width=120,
                command=lambda u=user: self.select_user(u)
            )
            btn.pack(pady=5)
            self.user_buttons.append(btn)

    # ============================================================== #
    #                SELECT USER (PRIVATE CHAT)                      #
    # ============================================================== #
    def select_user(self, username):
        self.target_user = username

        for widget in self.chat_frame.winfo_children():
            widget.destroy()

        if username not in self.chat_history:
            self.chat_history[username] = []

        for msg, sender in self.chat_history[username]:
            self.add_bubble(msg, "right" if sender == "you" else "left")

        if username == "everyone":
            self.add_bubble("💬 Chat mode: Everyone", "left")
        else:
            self.add_bubble(f"💬 Private chat with: {username}", "left")

    # ============================================================== #
    #               STORE + DISPLAY BUBBLE MESSAGE                  #
    # ============================================================== #
    def show_message(self, msg, target="everyone", sender="other"):
        if target not in self.chat_history:
            self.chat_history[target] = []

        self.chat_history[target].append((msg, sender))

        if self.target_user == target:
            side = "right" if sender == "you" else "left"
            self.add_bubble(msg, side)

    # ============================================================== #
    #                       SEND MESSAGE                             #
    # ============================================================== #
    def send_clicked(self):
        msg = self.message_entry.get().strip()
        if msg == "":
            return

        if not self.client.connected:
            self.add_bubble("⚠️ ERROR: Not connected.", "left")
            return

        if self.target_user == "everyone":
            self.show_message(f"You: {msg}", "everyone", sender="you")
            self.client.send_message(msg)
        else:
            self.show_message(f"You → {self.target_user}: {msg}", self.target_user, sender="you")
            self.client.send_message(f"SEND_TO:{self.target_user}:{msg}")

        self.message_entry.delete(0, "end")

    # ============================================================== #
    #                       USERNAME POPUP                           #
    # ============================================================== #
    def ask_username(self):
        popup = ctk.CTkInputDialog(text="Enter your username:", title="Username")
        username = popup.get_input()

        if not username:
            username = "Guest"

        self.client.username = username
        self.client.send_message(username)
        self.add_bubble(f"✔ Logged in as: {username}", "left")


# ========================================================== #
#                           RUN                              #
# ========================================================== #
if __name__ == "__main__":
    ChatGUI()
