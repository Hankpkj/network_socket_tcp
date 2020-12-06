import os
import sys
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button
import socket
import threading
from tkinter import messagebox


class ClientSide:
    client_socket = None
    last_received_message = None

    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.name_space = None
        self.ip_space = None
        self.port_space = None
        self.file_space = None
        self.enter_text_widget = None
        self.join_button = None
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = '127.0.0.1'
        remote_port = 9999
        remote_port_file = 9900
        self.client_socket.connect((remote_ip, remote_port))
        self.client_socket.connect((remote_ip, remote_port_file))

    def initialize_gui(self):
        self.root.title("Socket Chat")
        self.root.resizable(0, 0)
        self.display_chat_box()
        self.display_ip_section()
        self.display_port_section()
        self.display_name_section()
        self.display_file()
        self.display_chat_entry_box()

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()
    #     thread_file = threading.Thread(target=self.receive_file_from_server, args=(self.client_socket))
    #
    # def receive_file_from_server(self, so):
    #     while True:


    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(1024)
            if not buffer:
                break
            message = buffer.decode('utf-8')

            if "joined" in message:
                user = message.split(":")[1]
                message = user + " has joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)

        so.close()

    def display_name_section(self):
        frame = Frame()
        Label(frame, text='Enter your name:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_space = Entry(frame, width=50, borderwidth=2)
        self.name_space.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="Join", width=10, command=self.usr_connect).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_ip_section(self):
        frame = Frame()
        Label(frame, text='Enter ip:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.ip_space = Entry(frame, width=50, borderwidth=2)
        self.ip_space.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="fix", width=10, command=self.block_ip).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_port_section(self):
        frame = Frame()
        Label(frame, text='Enter port', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.port_space = Entry(frame, width=50, borderwidth=2)
        self.port_space.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="fix", width=10, command=self.block_port).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_chat_box(self):
        frame = Frame()
        Label(frame, text='Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    def display_file(self):
        frame = Frame()
        Label(frame, text='Enter filename:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.file_space = Entry(frame, width=50, borderwidth=2)
        self.file_space.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="send", width=10, command=self.send_file).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def send_file(self):
        file_name = self.file_space.get()
        self.client_socket.sendall(file_name.encode('utf-8'))
        data = self.client_socket.recv(1024)
        data_transferred = 0

        if not data:
            print('could not find %s' % file_name)
            sys.exit()

        dir_path = os.getcwd()
        with open(dir_path + "\\" + file_name, 'wb') as f:
            try:
                while data:
                    f.write(data)
                    data_transferred += len(data)
                    data = self.client_socket.recv(1024)
            except Exception as ex:
                print(ex)
        print('file %s send complete.  %d Kb' % (file_name, data_transferred))

    def block_ip(self):
        if len(self.ip_space.get()) == 0:
            messagebox.showerror(
                "Enter ip address dd", self.ip_space.get()
            )
            return
        elif self.ip_space.get() != '127.0.0.1':
            messagebox.showerror(
                "Enter ip address", self.ip_space.get()
            )
            return
        self.ip_space.config(state='disabled')

    def block_port(self):
        if len(self.port_space.get()) == 0:
            messagebox.showerror(
                "Enter port number", "eg. 9999"
            )
            return
        elif self.port_space.get() != '9999':
            messagebox.showerror(
                "Enter port number", "eg. 9999"
            )
            return
        self.port_space.config(state='disabled')

    def usr_connect(self):
        if len(self.name_space.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return

        self.name_space.config(state='disabled')
        self.client_socket.send(("joined:" + self.name_space.get()).encode('utf-8'))

    def on_enter_key_pressed(self, event):
        if len(self.name_space.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        senders_name = self.name_space.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)


if __name__ == '__main__':
    root = Tk()
    gui = ClientSide(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()