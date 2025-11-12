import socket
import threading
from tkinter import *
from tkinter import scrolledtext
from tkinter import simpledialog

# Create socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# ------------------- GUI PART -------------------

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat App")
        self.master.geometry("400x500")

        self.chat_area = scrolledtext.ScrolledText(master, wrap=WORD)
        self.chat_area.pack(padx=10, pady=10, fill=BOTH, expand=True)
        self.chat_area.config(state=DISABLED)

        self.msg_entry = Entry(master)
        self.msg_entry.pack(padx=10, pady=5, fill=X)
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_button = Button(master, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=5, fill=X)

        self.running = True

        # Ask nickname
        self.nickname = simpledialog.askstring("Nickname", "Choose your nickname", parent=master)
        self.connect_to_server()

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def connect_to_server(self):
        try:
            # Connect to your cloud server IP (replace below)
            client.connect(('YOUR_CLOUD_IP', 12345))
            print("Connected to server!")
        except:
            print("Connection failed.")
            self.master.quit()

    def receive(self):
        while self.running:
            try:
                msg = client.recv(1024).decode()
                if msg == 'NICK':
                    client.send(self.nickname.encode())
                else:
                    self.chat_area.config(state=NORMAL)
                    self.chat_area.insert(END, msg + "\n")
                    self.chat_area.yview(END)
                    self.chat_area.config(state=DISABLED)
            except:
                print("Connection closed.")
                client.close()
                break

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        self.msg_entry.delete(0, END)
        client.send(f"{self.nickname}: {msg}".encode())

# ------------------- RUN APP -------------------

root = Tk()
gui = ChatClient(root)
root.mainloop()
