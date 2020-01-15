
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
    if 'REQUEST id' in data:
        client.send(DEVICE_ID.encode('UTF-8'))
        wait_response = client.recv(1024).decode('UTF-8')
        print(wait_response)
        break

# REQUEST TYPE - DATA TYPE - DATA SOURCE - DATA NAME - DATA DESTINATION
client.send('REQUEST client-0001 name client-0001;'.encode('UTF-8'))
print(client.recv(1024).decode('UTF-8'))
client.send('REQUEST client-0001 media_extension client-0001;'.encode('UTF-8'))
print(client.recv(1024).decode('UTF-8'))
client.send('REQUEST client-0001 media_last_update client-0001;'.encode('UTF-8'))
print(client.recv(1024).decode('UTF-8'))
client.send('REQUEST server-0001 media_files client-0001;'.encode('UTF-8'))
print(client.recv(1024).decode('UTF-8'))
client.send('SET server-0001 media_files [1, 0.001] client-0001;'.encode('UTF-8'))
print(client.recv(1024).decode('UTF-8'))
client.send('SET server-0001 file_path hello client-0001;'.encode('UTF-8'))
print(client.recv(1024).decode('UTF-8'))
client.send('UPDATE client-0001;'.encode('UTF-8'))
print(client.recv(1024).decode('UTF-8'))

time.sleep(1000)
client.detach()
client.close()
