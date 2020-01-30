
import threading
import socket
import os


# Const Variables
MAX_CONNECTIONS = 50
CONNECTION_PORT = 12345
BUFFER_SIZE = 1024


class ClientThread(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)
        print('[+] Stating Thread For (%s:%s)' % connection.getsockname())
        self.connection = connection
        self.update = True

    def send_data(self, data):
        data = '%s;' % data
        self.connection.send(data.encode())

    def get_data(self):
        data = ''
        while ';' not in data:
            data += self.connection.recv(BUFFER_SIZE).decode()
        data = data[:-1]
        return data

    def run(self):
        while True:
            request = self.get_data()

            if request[:3] == 'id=':
                self.id = request[3:]
                self.send_data('id set')
                clients[self.id] = self
            elif request == 'update media':
                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.mp4')
                file_size = os.path.getsize(file_path)
                file_data = open(file_path, 'rb').read()

                self.send_data(str(file_size))
                self.get_data()

                self.connection.send(file_data)
                self.send_data('EOF OCCURED')
                self.get_data()
                self.send_data('acknowledged')
                self.update = False
            elif request == 'update?':
                if self.update:
                    self.send_data('yes')
                else:
                    self.send_data('no')
            elif request[:6] == 'update':
                device = request[7:]
                if device in clients:
                    clients[device].update = True
                else:
                    pass  # Device is Offline, Will Check Next Boot Anyways
                self.send_data('ok')
            else:
                self.connection.send(('%s;' % request).encode())


        print('[-] Killing Thread For (%s:%s)' % self.connection.getsockname())
        self.connection.close()  # Kill Connection


server_connection = socket.socket()
server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_connection.bind(('', CONNECTION_PORT))
server_connection.listen(MAX_CONNECTIONS)

clients = {}

while True:
    client_connection, address = server_connection.accept()
    client_thread = ClientThread(client_connection)
    client_thread.run()