import socket
import threading
import pickle
import re
from tkinter import *
from tkinter.scrolledtext import *
from tkinter.simpledialog import *
from tkinter.messagebox import *
from tkinter.ttk import *

class OpeningDialog(Dialog):

    def body(self, master):
        self.result1 = None
        self.result2 = None
        self.result3 = None

        Label(master, text="IP:").grid(row=0, pady=2, padx=2, sticky=E)
        Label(master, text="Port:").grid(row=1, pady=2, padx=2, sticky=E)
        Label(master, text="Nickname:").grid(row=2, pady=2, padx=2, sticky=E)

        self.e1 = Entry(master)
        self.e2 = Entry(master)
        self.e3 = Entry(master)

        self.e1.grid(row=0, column=1, pady=2, padx=2)
        self.e2.grid(row=1, column=1, pady=2, padx=2)
        self.e3.grid(row=2, column=1, pady=2, padx=2)


    def apply(self):
        self.result1 = self.e1.get()
        self.result2 = self.e2.get()
        self.result3 = self.e3.get()


class Client:
    
    def __init__(self):
        msg = Tk()
        msg.withdraw()
        self.fields_entered = False
        self.connected = False

        opening = OpeningDialog(msg, title="Connect to a chatroom")

        while not self.fields_entered:
            if '' in {opening.result1, opening.result2, opening.result3}:
                showwarning("Warning", message='Missing field(s)')
                opening = OpeningDialog(msg, title="Connect to a chatroom")
                continue
            self.fields_entered = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while not self.connected:
            if all(x is None for x in [opening.result1, opening.result2, opening.result3]):
                exit(0)
            try:
                self.sock.connect((opening.result1, int(opening.result2)))
                self.connected = True
                print("Chatroom found!")
            except:
                showwarning("Warning", message="Unable to connect to server")
                opening = OpeningDialog(msg, title="Connect to a chatroom")
        self.nickname = opening.result3.replace('\n','')

        self.gui_done = False
        self.running = True
        self.nick_list = []
        self.nicks_done = False
        self.message_queue = []

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        message_thread = threading.Thread(target=self.handle_messages)

        gui_thread.start()
        receive_thread.start()
        message_thread.start()

    def gui_loop(self):
        self.win = Tk()
        self.win.title('Chatroom')

        self.win.rowconfigure(1, weight=1)
        self.win.columnconfigure(0, weight=1)

        self.chat_label = Label(self.win, text="Chat")
        self.chat_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.text_area = ScrolledText(self.win, font=('Sergoe UI', 10))
        self.text_area.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=N+E+W+S)
        self.text_area.config(state='disabled')

        self.input_area = Entry(self.win)
        self.input_area.focus()
        self.input_area.grid(row=3, column=0, padx=5, pady=5, sticky=W+E)

        self.send_button = Button(self.win, text='Send', command=self.write)
        self.send_button.grid(row=3, column=1, padx=5, pady=5)

        self.nick_label = Label(self.win, text='Online')
        self.nick_label.grid(row=0, column=2, padx=5, pady=5)

        self.nick_listbox = Listbox(self.win)
        self.nick_listbox.grid(row=1, column=2, rowspan=3, padx=5, pady=5, sticky=N+S)

        self.gui_done = True

        self.win.bind('<Return>', lambda event:self.write())

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        if re.sub(r"[\n\t\s]*", "", self.input_area.get()) != '':
            message = f"{self.nickname}: {self.input_area.get()}\n"
            self.sock.send(pickle.dumps(message))
            self.input_area.delete(0, 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)
    
    def update_nicks(self):
        if self.gui_done:
            print("Nicks updated")
            self.nicks_done = True
            self.nick_listbox.delete(0,'end')
            for nick in self.nick_list:
                self.nick_listbox.insert(END, nick)

    def receive(self):
        while self.running:
            try:              
                message = pickle.loads(self.sock.recv(1024))
                self.message_queue.append(message)
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break
    
    def handle_messages(self):
        while self.running:
            if self.gui_done:
                for message in self.message_queue:
                    if message == 'NICK':
                        self.sock.send(pickle.dumps(self.nickname))
                    elif isinstance(message, list):
                        self.nick_list = message
                        self.update_nicks()
                    else:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
                    self.message_queue.remove(message)

client = Client()
