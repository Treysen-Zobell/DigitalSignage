
import socket
import time
import tqdm
import os

DEVICE_ID = '000001'
DEVICE_TYPE = 'display'
SERVER_IP = socket.gethostname()  # Localhost


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


server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        server_connection.connect((socket.gethostname(), 12345))
        break
    except ConnectionRefusedError:
        print('[E] Server is Inaccessible, Attempting Again in 10s')
        time.sleep(10)
id_request = DataTransfer.receive_data(server_connection)
DataTransfer.send_id(server_connection, DEVICE_ID)
DataTransfer.receive_data(server_connection)
DataTransfer.send_data(server_connection, DEVICE_TYPE)
DataTransfer.receive_data(server_connection)

# FileTransfer.receive_file(connection, 'new_test.mp4')
