
import socket
import time

SERVER_KEY = 'server-0001'
DEVICE_ID = 'device-0001'


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

client.send(('%s REQUEST data;' % DEVICE_ID).encode('UTF-8'))
client.send('GIVE ME DATA;'.encode('UTF-8'))

client.detach()
client.close()
time.sleep(10)
