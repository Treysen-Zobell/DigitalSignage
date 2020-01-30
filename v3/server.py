
import threading
import socket
import tqdm
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
        if filename[0] == '.':
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename[2:])
        file_size = os.path.getsize(filename)
        file_data = open(filename, 'rb').read()

        # Transmit Data
        print('[+] Transmitting File to (%s:%s)' % socket_connection.getsockname())
        print('Sending File Size %s' % file_size)
        DataTransfer.send_data(socket_connection, str(file_size))
        print('File Size Sent')
        print(socket_connection.recv(1024))
        print('File Size Received')
        print('Sending File')
        socket_connection.send(file_data)
        print(socket_connection.recv(1024))
        print('[-] Done Transmitting File to (%s:%s)' % socket_connection.getsockname())

    @staticmethod
    def receive_file(socket_connection, filename):
        DataTransfer.send_next(socket_connection)
        print('Waiting For File Size')
        file_size = int(DataTransfer.receive_data(socket_connection))
        print('file_size=%i' % file_size)
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
    def __init__(self, client_connection, client_id):
        threading.Thread.__init__(self)
        self.connection = client_connection
        self.client_id = client_id
        self.should_update = True

    def run(self):
        print('[+] Stating Client Thread For %s' % self.client_id)
        while True:
            request = DataTransfer.receive_data(self.connection)
            print(request)
            DataTransfer.send_data(self.connection, request)


class ManagerThread(threading.Thread):
    def __init__(self, client_connection, client_id, server_thread):
        threading.Thread.__init__(self)
        self.connection = client_connection
        self.client_id = client_id
        self.server_thread = server_thread
        self.should_update = True

    def run(self):
        print('[+] Stating Client Thread For %s' % self.client_id)
        while True:
            request = DataTransfer.receive_data(self.connection)
            fields = request.split(' ')

            if fields[0] == 'set':
                print('destination=%s' % fields[1])
                print('field=%s' % fields[2])
                print('value=%s' % fields[3])

                if fields[1] in self.server_thread.clients:
                    print(self.server_thread.clients)
                else:
                    print(self.server_thread.clients)

            print(fields)
            DataTransfer.send_data(self.connection, request)


class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.listen_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_connection.bind(('', 12345))
        self.listen_connection.listen(MAX_CONNECTIONS)
        self.clients = {}

    def run(self):
        while True:
            client_connection, (ip, port) = self.listen_connection.accept()  # Device Tried To Connect
            client_id = DataTransfer.request_id(client_connection)  # On Connect Request ID
            DataTransfer.send_data(client_connection, client_id)  # Echo Id Back To Client
            client_type = DataTransfer.receive_data(client_connection)  # Get If Client Is Display Or Manager
            DataTransfer.send_next(client_connection)  # Client Is Waiting, Send Next To Allow It To Continue

            if client_type == 'display':
                client_thread = ClientThread(client_connection, ('%s-%s' % (client_type, client_id)))
                client_thread.run()
                self.clients['%s-%s' % (client_type, client_id)] = client_thread
            elif client_type == 'manager':
                manager_thread = ManagerThread(client_connection, ('%s-%s' % (client_type, client_id)), self)
                manager_thread.run()

            print('%s-%s connected on (%s:%s)' % (client_type, client_id, ip, port))

            # print('Transferring File')
            # FileTransfer.transmit_file(client_connection, './test.mp4')


server_thread = ServerThread()
server_thread.run()


