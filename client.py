
import socket
import time
import os

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


def receive_file(filename):
    file_size = int(client.recv(1024).decode())
    print(file_size)
    current_size = 0
    file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), 'wb')
    while current_size < file_size:
        segment = client.recv(1024)
        file.write(segment)
        current_size += 1024
    file.close()


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
    data = client.recv(1024).decode()
    if 'REQUEST id' in data:
        client.send(DEVICE_ID.encode())
        wait_response = client.recv(1024).decode()
        print(wait_response)
        break

# REQUEST TYPE - DATA DESTINATION - DATA NAME - DATA SOURCE
client.send('REQUEST client-0001 name client-0001;'.encode())
print(client.recv(1024).decode())
client.send('REQUEST client-0001 media_extension client-0001;'.encode())
print(client.recv(1024).decode())
client.send('REQUEST client-0001 media_last_update client-0001;'.encode())
print(client.recv(1024).decode())
client.send('REQUEST server-0001 media_files client-0001;'.encode())
print(client.recv(1024).decode())
client.send('SET server-0001 media_files [1, 0.001] client-0001;'.encode())
print(client.recv(1024).decode())
client.send('SET server-0001 file_path hello client-0001;'.encode())
print(client.recv(1024).decode())
client.send('UPDATE client-0001;'.encode())
print(client.recv(1024).decode())

client.send('TRANSFER ./test.mp4 TO client-0001;'.encode())
receive_file('new_test.mp4')

client.detach()
client.close()
