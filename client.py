
import subprocess
import threading
import datetime
import socket
import shutil
import time
import tqdm
import cec
import os

DEVICE_ID = '000001'
DEVICE_TYPE = 'display'
SERVER_IP = '192.168.1.8'


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
        socket_connection.setblocking(False)
        data = ''
        while ';' not in data:
            try:
                data += socket_connection.recv(1024).decode()
            except BlockingIOError:
                pass
        data = data[:-1]
        socket_connection.setblocking(True)
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
        DataTransfer.send_next(socket_connection)
        print('Waiting For File Size')
        file_size = int(DataTransfer.receive_data(socket_connection))
        print('file_size=%i' % file_size)
        DataTransfer.send_next(socket_connection)

        socket_connection.settimeout(3)
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
        socket_connection.settimeout(10)


class ScreenOnOffController(threading.Thread):
    def __init__(self,):
        threading.Thread.__init__(self)
        self.tv = cec.Device(cec.CECDEVICE_TV)
        self.on = True

    def run(self):
        self.start = datetime.time(7, 0, 0, 0)
        self.end = datetime.time(17, 0, 0, 0)
        cec.init()
        self.tv.power_on()
        self.on = True
        while True:
            if self.should_be_on():
                if not self.on:
                    self.tv.power_on()
                    self.on = True
            else:
                if self.on:
                    self.tv.standby()
                    self.on = False
            time.sleep(60)

    def should_be_on(self):
        now = datetime.datetime.now().time()

        if self.start <= self.end:
            return self.start <= now <= self.end
        else:
            return self.start <= now or now <= self.end


time.sleep(15)
server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        server_connection.connect((SERVER_IP, 12345))
        break
    except ConnectionRefusedError:
        print('[E] Server is Inaccessible, Attempting Again in 10s')
        time.sleep(10)
    except OSError:
        print('[E] Network Not Ready Yes, Attempting Again in 10s')
        time.sleep(10)
id_request = DataTransfer.receive_data(server_connection)
DataTransfer.send_id(server_connection, DEVICE_ID)
DataTransfer.receive_data(server_connection)
DataTransfer.send_data(server_connection, DEVICE_TYPE)
DataTransfer.receive_data(server_connection)

screen_controller = ScreenOnOffController()
screen_controller.start()

while True:
    try:
        DataTransfer.send_data(server_connection, 'get %s-%s should_update' % (DEVICE_TYPE, DEVICE_ID))
        should_update = 'true' in DataTransfer.receive_data(server_connection)
        if should_update:
            DataTransfer.send_data(server_connection, 'set %s-%s should_update false' % (DEVICE_TYPE, DEVICE_ID))
            print('Would Update Now')
            DataTransfer.receive_data(server_connection)
            DataTransfer.send_data(server_connection, 'get %s-%s media_name' % (DEVICE_TYPE, DEVICE_ID))
            media_name = DataTransfer.receive_data(server_connection)
            print('media_name=%s' % media_name)
            DataTransfer.send_data(server_connection, 'request %s-%s file %s' % (DEVICE_TYPE, DEVICE_ID, media_name))
            DataTransfer.receive_data(server_connection)
            FileTransfer.receive_file(server_connection, '/home/pi/DigitalSignage/media.mp4.tmp')
            os.system('killall vlc')
            shutil.copyfile('/home/pi/DigitalSignage/media.mp4.tmp', '/home/pi/DigitalSignage/media.mp4')
            subprocess.Popen(['cvlc', '-f', '--loop', '--video-on-top', '/home/pi/DigitalSignage/media.mp4'])
            
        print(should_update)
        time.sleep(5)
    except ConnectionResetError:
        server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_connection.connect((SERVER_IP, 12345))
            os.system('reboot')
            break
        except ConnectionRefusedError:
            print('[E] Server is Inaccessible, Attempting Again in 10s')
            time.sleep(10)
    except BrokenPipeError:
        os.system('reboot')
