
import threading
import socket
import json
import os

BUFFER = 1024
ID = 'server-0001'


class Data:
    def __init__(self):
        self.clients = {}
        self.clients = self.load_json_clients()

    @staticmethod
    def load_media_list():
        media_files = [f for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Media'))
                       if os.path.isfile(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Media'), f))]
        return media_files

    def save_json_clients(self, json_clients):
        for json_client in json_clients:
            json_clients[json_client]['thread'] = 'disconnected'
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clients.json'), 'w+') as json_file:
            json.dump(self.clients, json_file)

    @staticmethod
    def load_json_clients():
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clients.json')) as json_file:
            json_data = json.load(json_file)
            json_clients = {}
            for client in json_data:
                json_clients[client] = json_data[client]
        return json_clients


class ClientThread(threading.Thread):
    def __init__(self, connection, data):
        print('[+] Starting Thread (%s:%s)' % connection.getsockname())
        threading.Thread.__init__(self)

        self.connection = connection
        self.data = data

        self.running = True
        self.id = ''

        self.connect()

    def run(self):
        try:
            while self.running:
                data_in = self.connection.recv(BUFFER).decode('UTF-8')
                self.data.clients[self.id]['data_buffer'] += data_in

        except ConnectionResetError:
            self.data.clients[self.id]['thread'] = 'disconnected'

        print('[-] Killing Thread (%s:%s)' % self.connection.getsockname())

    def connect(self):
        self.connection.send('REQUEST id'.encode('UTF-8'))
        self.id = self.connection.recv(BUFFER).decode('UTF-8')
        if self.id in self.data.clients:
            self.connection.send('ID VALID CONNECTION ACCEPTED'.encode('UTF-8'))
            self.data.clients[self.id]['thread'] = self
        else:
            self.connection.send('ID INVALID CONNECTION DENIED'.encode('UTF-8'))
            self.running = False

    def execute(self, command):
        print('command = "%s"' % command)
        print('')

        if command[:7] == 'REQUEST':
            print('command[:7] = "%s"' % command[:7])  # Base Command
            print('command[8:19] = "%s"' % command[8:19])  # Source
            print('command[20:-12] = "%s"' % command[20:-12])  # Data Name
            print('command[-11:] = "%s"' % command[-11:])  # Destination

            self.data.clients[command[-11:]]['thread'].connection.send(str(self.data.clients[command[8:19]][command[20:-12]]).encode('UTF-8'))
        elif command[:3] == 'SET':
            destination = command[4:15]
            data_field = command[16:command[16:].find(' ')+16]
            data = command[command[16:].find(' ')+17:-12]
            origin = command[-11:]

            print('command[:3] = "%s"' % command[:3])
            print('command[4:15] = "%s"' % destination)
            print('command[16:command[16:].find(' ')+16] = "%s"' % data_field)
            print('command[-11:] = "%s"' % origin)

            # If Is List, Convert From Sting To List
            if data[0] == "[":
                data = data[1:-1]
                data = data.split(', ')

            # Fix Variable Type
            if data is list:
                for i in range(len(data)):
                    if data[i][0] == '"':
                        data[i] = data[i][1:-1]
                    elif data[i].lower() == "true" or data[i] == "false":
                        data[i] = 'true' in data[i].lower()
                    else:
                        data[i] = float(data[i])

            self.data.clients[destination][data_field] = data
            self.data.clients[origin]['thread'].connection.send('DATA ALTERED'.encode('UTF-8'))

            print('self.data.clients[destination][data_field] = %s' % self.data.clients[destination][data_field])
            print()

        elif command[:6] == 'UPDATE':
            self.data.clients[command[7:]]['thread'].connection.send('UPDATE'.encode('UTF-8'))


class CommandParser(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data

    def run(self):
        while True:
            for client in self.data.clients:
                command_buffer = self.data.clients[client]['data_buffer']
                if ';' in command_buffer:
                    command = command_buffer[:command_buffer.find(';')]
                    self.data.clients[client]['data_buffer'] = command_buffer[command_buffer.find(';')+1:]
                    self.data.clients[client]['thread'].execute(command)


tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((socket.gethostname(), 2004))

data_store = Data()
command_parser = CommandParser(data_store)
command_parser.start()

while True:
    tcp_server.listen(50)
    client_connection, (ip, port) = tcp_server.accept()
    client_thread = ClientThread(client_connection, data_store)
    client_thread.start()
