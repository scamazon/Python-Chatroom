import threading
import socket
import pickle
import re
import random
import colorsys
from datetime import datetime

HOST = socket.gethostbyname(socket.gethostname())
PORT = 42069

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()


clients = []
nicknames = []
addresses = []
colors = []

def random_color():
    color = colorsys.hsv_to_rgb(random.random(), 0.82, 171)
    return (int(color[0]),int(color[1]),int(color[2]))

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            index = clients.index(client)
            nickname = nicknames[index]
            color = colors[index]
            message_raw = pickle.loads(client.recv(1024))
            if re.sub(r"[\n\t\s]*", "", message_raw) != '':
                message = [color, f'{nickname}: {message_raw}\n']
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {message[1]}".strip())
                broadcast(pickle.dumps(message))
        except:
            timestamp = datetime.now().strftime("%H:%M:%S")
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            address = addresses[index]
            color = colors[index]
            broadcast(pickle.dumps([(200,0,0),f'{nickname} left the chat\n']))
            print(f"[{timestamp}] {nickname} disconnected.")
            nicknames.remove(nickname)
            addresses.remove(address)
            colors.remove(color)
            update_nicks()
            break

def update_nicks():
    nick_list = pickle.dumps(nicknames)
    broadcast(nick_list)

def receive():
    while True:
        client, address = server.accept()
        if address[0] in addresses:
            client.close()
            print(f'Client denied (client already exists on ip address {address[0]})')
            continue

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Client connected {str(address)}")

        client.send(pickle.dumps('NICK'))
        try:
            nickname = pickle.loads(client.recv(1024))
            color = random_color()

            nicknames.append(nickname)
            clients.append(client)
            addresses.append(address[0])
            colors.append(color)

            print(f'Nickname of the client is {nickname}.')
            update_nicks()
            client.send(pickle.dumps([(0,0,0),'Connected to the server\n']))
            broadcast(pickle.dumps([(0,200,0),f'{nickname} joined the chat\n']))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except:
            print('User error')

print(f'Hosting on {HOST}')
print('Server is listening...')
receive()
