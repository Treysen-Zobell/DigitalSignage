
import threading
import socket
import tqdm
import json
import os

MAX_CONNECTIONS = 50


class DataTransfer:
    @staticmethod
    def send_data(socket_connection, data):
        data = data + ';'
        socket_connection.send(data.encode())

    @staticmethod
    def send_next(socket_connection):
        socket_connection.send('null;'.encode())

    @staticmethod
    def receive_data(socket_connection):
        data = ''
        while ';' not in data:
            data += socket_connection.recv(1024).decode()
        data = data[:-1]
        return data

    @staticmethod
    def send_id(socket_connection, client_id):
        DataTransfer.send_data(socket_connection, client_id)

    @staticmethod
    def request_id(socket_connection):
        DataTransfer.send_data(socket_connection, 'request id')
        client_id = DataTransfer.receive_data(socket_connection)
        return client_id


class FileTransfer:
    @staticmethod
    def transmit_file(socket_connection, filename):
        DataTransfer.receive_data(socket_connection)
        file_size = os.path.getsize(filename)
        file_data = open(filename, 'rb').read()

        # Transmit Data
        DataTransfer.send_data(socket_connection, str(file_size))
        socket_connection.recv(1024)
        socket_connection.send(file_data)
        socket_connection.recv(1024)

    @staticmethod
    def receive_file(socket_connection, filename):
        DataTransfer.send_next(socket_connection)
        file_size = int(DataTransfer.receive_data(socket_connection))
        DataTransfer.send_next(socket_connection)

        socket_connection.settimeout(5)
        progress = tqdm.tqdm(range(file_size), 'Receiving File', unit='B', unit_scale=True, unit_divisor=1024)
        with open(filename, 'wb') as file:
            for _ in progress:
                try:
                    bytes_read = socket_connection.recv(4096)
                except socket.timeout:
                    break
                if not bytes_read:
                    break
                file.write(bytes_read)
                progress.update(len(bytes_read))
        DataTransfer.send_next(socket_connection)


class ClientThread(threading.Thread):
    def __init__(self, client_connection, client_id, server_thread_in):
        threading.Thread.__init__(self)
        self.connection = client_connection
        self.client_id = client_id
        self.server_thread = server_thread_in
        self.should_update = True
        self.media_name = self.server_thread.json_clients[self.client_id]['media_name']

    def run(self):
        try:
            print('[+] Stating Client Thread For %s' % self.client_id)
            while True:
                request = DataTransfer.receive_data(self.connection)
                fields = request.split(' ')

                if fields[0] == 'get':
                    if fields[1] in self.server_thread.clients:
                        if fields[2] == 'should_update':
                            if self.should_update:
                                DataTransfer.send_data(self.server_thread.clients[fields[1]].connection, 'true')
                            else:
                                DataTransfer.send_data(self.server_thread.clients[fields[1]].connection, 'false')
                        if fields[2] == 'media_name':
                            DataTransfer.send_data(self.server_thread.clients[fields[1]].connection, self.server_thread.clients[fields[1]].media_name)
                    elif fields[1] in self.server_thread.json_clients:
                        DataTransfer.send_next(self.server_thread.json_clients[fields[1]][fields[2]])
                        self.server_thread.json_clients[fields[1]][fields[2]] = fields[3]

                if fields[0] == 'set':
                    if fields[1] in self.server_thread.clients:
                        if fields[2] == 'should_update':
                            self.server_thread.clients[fields[1]].should_update = 'true' in fields[3].lower()
                            DataTransfer.send_next(self.connection)
                        if fields[2] == 'media_name':
                            self.server_thread.clients[fields[1]].media_name = fields[3]
                            DataTransfer.send_next(self.connection)

                    if fields[1] in self.server_thread.json_clients:
                        self.server_thread.json_clients[fields[1]][fields[2]] = fields[3]

                if fields[0] == 'request':
                    if fields[1] in self.server_thread.clients:
                        if fields[2] == 'file':
                            DataTransfer.send_next(self.connection)
                            FileTransfer.transmit_file(self.connection, fields[3])

                if fields[0] == 'command':
                    if fields[1] == 'save':
                        with open('clients.json', 'w') as json_file:
                            json.dump(self.server_thread.clients, json_file)
                    if fields[1] == 'close':
                        break

            print('[-] Killing Client Thread For %s' % self.client_id)
        except ConnectionResetError:
            print('[-] Client Closed Unexpectedly %s' % self.client_id)


class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.listen_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_connection.bind(('', 12345))
        self.listen_connection.listen(MAX_CONNECTIONS)
        self.clients = {}

        with open('clients.json', 'r') as json_file:
            self.json_clients = json.load(json_file)

    def run(self):
        while True:
            client_connection, (ip, port) = self.listen_connection.accept()  # Device Tried To Connect
            client_id = DataTransfer.request_id(client_connection)  # On Connect Request ID
            DataTransfer.send_data(client_connection, client_id)  # Echo Id Back To Client
            client_type = DataTransfer.receive_data(client_connection)  # Get If Client Is Display Or Manager
            DataTransfer.send_next(client_connection)  # Client Is Waiting, Send Next To Allow It To Continue

            client_thread = ClientThread(client_connection, ('%s-%s' % (client_type, client_id)), self)
            client_thread.start()
            self.clients['%s-%s' % (client_type, client_id)] = client_thread

            print('%s-%s connected on (%s:%s)' % (client_type, client_id, ip, port))


server_thread = ServerThread()
server_thread.start()
