
import tqdm
import os


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
