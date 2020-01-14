
import socket
import time

DEVICE_ID = 'client-0001'


class Client:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.location = ''
        self.timetable = []
        self.media_name = ''
        self.media_extension = ''
        self.media_last_update = ''

        self.online = False
        self.ip = ''


host = socket.gethostname()
ip = socket.gethostbyname(host)
port = 2004
buffer_size = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        client.connect((host, port))
        break
    except ConnectionRefusedError:
        print('[E] Server is Inaccessible, Attempting Again in 10s')
        time.sleep(10)

while True:
    data = client.recv(1024).decode('UTF-8')
    if 'REQUEST:ID' in data:
        client.send(DEVICE_ID.encode('UTF-8'))
        wait_response = client.recv(1024).decode('UTF-8')
        print(wait_response)
        break

client.send('REQUEST name;'.encode('UTF-8'))
name = client.recv(1024).decode('UTF-8')
print(name)

client.send('REQUEST media_extension;'.encode('UTF-8'))
media_extension = client.recv(1024).decode('UTF-8')
print(media_extension)

client.send('REQUEST media_last_update;'.encode('UTF-8'))
media_last_update = client.recv(1024).decode('UTF-8')
print(media_last_update)

client.detach()
client.close()
time.sleep(10)
