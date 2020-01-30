
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
        socket_connection.send('null'.encode())

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
        if filename[0] == '.':
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename[2:])
        file_size = os.path.getsize(filename)
        file_data = open(filename, 'rb').read()

        # Transmit Data
        print('[+] Transmitting File to (%s:%s)' % socket_connection.getsockname())
        print('Sending File Size')
        DataTransfer.send_data(socket_connection, str(file_size))
        print(socket_connection.recv(1024))
        print('File Size Received')
        print('Sending File')
        socket_connection.send(file_data)
        print(socket_connection.recv(1024))
        print('[-] Done Transmitting File to (%s:%s)' % socket_connection.getsockname())

    @staticmethod
    def receive_file(socket_connection, filename):
        print('Waiting For File Size')
        file_size = int(DataTransfer.receive_data(socket_connection))
        print('file_size=%i' % file_size)
        DataTransfer.send_next(socket_connection)

        socket_connection.setblocking(False)
        progress = tqdm.tqdm(range(file_size), 'Receiving File', unit='B', unit_scale=True, unit_divisor=1024)
        with open(filename, 'wb') as file:
            for _ in progress:
                try:
                    bytes_read = socket_connection.recv(4096)
                except BlockingIOError:
                    break
                if not bytes_read:
                    break
                file.write(bytes_read)
                progress.update(len(bytes_read))
        DataTransfer.send_next(socket_connection)
        socket_connection.setblocking(True)


class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.listen_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_connection.bind((socket.gethostname(), 12345))
        self.listen_connection.listen(MAX_CONNECTIONS)

    def run(self):
        while True:
            client_connection, (ip, port) = self.listen_connection.accept()  # Device Tried To Connect
            client_id = DataTransfer.request_id(client_connection)  # On Connect Request ID
            DataTransfer.send_data(client_connection, client_id)  # Echo Id Back To Client
            client_type = DataTransfer.receive_data(client_connection)  # Get If Client Is Display Or Manager
            DataTransfer.send_next(client_connection)  # Client Is Waiting, Send Next To Allow It To Continue

            print('%s-%s connected on (%s:%s)' % (client_type, client_id, ip, port))


server_thread = ServerThread()
server_thread.run()


