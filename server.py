
import threading
import socket
import json
import os


clients = {}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clients.json')) as json_file:
    json_data = json.load(json_file)
    for client in json_data:
        print('%s HAS %s' % (client, str(json_data[client])))
        clients[client] = json_data[client]

media_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Media')
media = [f for f in os.listdir(media_path) if os.path.isfile(os.path.join(media_path, f))]
print(media)

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

        global clients
        self.client = clients[self.id]

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

    def execute(self, command):
        print('%s executes %s' % (self.id, command))
        if command[:12] == 'UPDATE MEDIA':
            global media, media_path
            media = [f for f in os.listdir(media_path) if os.path.isfile(os.path.join(media_path, f))]
            print(media)
        if command[:13] == 'REQUEST MEDIA':
            self.connection.send(('media IS %s' % str(media)).encode('UTF-8'))
        elif command[:7] == 'REQUEST':
            request = command[8:]
            self.connection.send(('%s IS %s' % (request, self.client[request])).encode('UTF-8'))
            print('%s IS %s' % (request, self.client[request]))


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

command_parser = CommandParser()
command_parser.start()
