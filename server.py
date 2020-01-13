
import threading
import socket
import time


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


client_threads = {}  # type is (client, client_thread)
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((socket.gethostname(), 2004))

data_buffer = {}  # type is (client_id, str)


class DataIn(threading.Thread):
    def __init__(self):
        print('[+] Starting Data In Server')
        threading.Thread.__init__(self)

    def run(self):
        while True:
            global tcp_server
            tcp_server.listen(50)
            connection, (ip, port) = tcp_server.accept()
            client_thread = ClientThread(connection, ip, port)
            global client_threads
            global data_buffer
            client_threads[client_thread.id] = client_thread
            data_buffer[client_thread.id] = ''
            client_thread.start()


class DataOut(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            print('data_buffer = %s' % str(data_buffer))
            time.sleep(1)


class ClientThread(threading.Thread):
    def __init__(self, connection, ip, port):
        print('[+] New Server Socket Thread Started For %s : %s' % (ip, str(port)))
        threading.Thread.__init__(self)

        self.ip = ip
        self.port = port
        self.connection = connection

        self.connection.send('REQUEST:ID'.encode('UTF-8'))
        self.id = connection.recv(1024).decode('UTF-8')
        connection.send('RECEIVED'.encode('UTF-8'))

    def run(self):
        try:
            while True:
                client_request = self.connection.recv(1024).decode('UTF-8')
                print('client_request = %s' % client_request)

                global data_buffer
                data_buffer[self.id] = data_buffer[self.id] + client_request
                print('data_buffer = %s' % str(data_buffer), flush=True)

        except ConnectionResetError:
            print('[!] %s Disconnected' % self.id)
            global client_threads
            del client_threads[self.id]
        print('[-] Server Socket Thread Terminated For %s : %s' % (self.ip, str(self.port)))
        print('data_buffer = %s' % str(data_buffer))

    def execute(self, command):
        print('%s executes %s' % (self.id, command))


class CommandParser(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global data_buffer
        while True:
            for key in data_buffer:
                if ';' in data_buffer[key]:
                    command = data_buffer[key][:data_buffer[key].find(';')]
                    data_buffer[key] = data_buffer[key][data_buffer[key].find(';')+1:]

                    global client_threads
                    client_threads[key].execute(command)


data_in_thread = DataIn()
data_in_thread.start()

data_out_thread = DataOut()
data_out_thread.start()

command_parser = CommandParser()
command_parser.start()
