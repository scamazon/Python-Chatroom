import threading
import socket
import pickle
from datetime import datetime

HOST = socket.gethostbyname(socket.gethostname())
PORT = 42069

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()


clients = []
nicknames = []
addresses = []


def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {pickle.loads(message)}".strip())
            broadcast(message)
        except:
            timestamp = datetime.now().strftime("%H:%M:%S")
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            address = addresses[index]
            broadcast(pickle.dumps(f'{nickname} left the chat\n'))
            print(f"[{timestamp}] {nickname} disconnected.")
            nicknames.remove(nickname)
            addresses.remove(address)
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

            nicknames.append(nickname)
            clients.append(client)
            addresses.append(address[0])

            print(f'Nickname of the client is {nickname}.')
            update_nicks()
            client.send(pickle.dumps('Connected to the server\n'))
            broadcast(pickle.dumps(f'{nickname} joined the chat\n'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except:
            print('User error')

print(f'Hosting on {HOST}')
print('Server is listening...')
receive()