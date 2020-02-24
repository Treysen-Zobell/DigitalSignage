
from CommandInterpreter import CommandInterpreter
from SocketTools import SocketTools

import threading
import socket
import json
import sys


# Client Thread
class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        print('[+] Starting Thread For (%s:%s)' % client_address)
        threading.Thread.__init__(self)
        self.socket = client_socket
        self.address = client_address
        self.mac_address = ''

    def run(self):
        try:
            self.type = SocketTools.receive(self.socket)[0]
            if self.type == 'client':
                self.mac_address = SocketTools.receive(self.socket)[0]
                try:
                    CommandInterpreter.data['%s_media' % self.mac_address]
                    CommandInterpreter.data['%s_timetable' % self.mac_address]
                    CommandInterpreter.data['%s_name' % self.mac_address]
                    CommandInterpreter.data['%s_should_update' % self.mac_address]
                except KeyError:
                    CommandInterpreter.data['%s_media' % self.mac_address] = 'Media/default.mp4'
                    CommandInterpreter.data['%s_timetable' % self.mac_address] = '07:00,22:00'
                    CommandInterpreter.data['%s_name' % self.mac_address] = 'default_name'
                    CommandInterpreter.data['%s_should_update' % self.mac_address] = 'True'
                    CommandInterpreter.interpret('save', self.socket)

                try:
                    with open(CommandInterpreter.data['%s_media' % self.mac_address], 'rb') as media_file:
                        media_data = media_file.read()
                except FileNotFoundError:
                    if CommandInterpreter.data['%s_media' % self.mac_address] == 'Media/default.mp4':
                        print('[E] Critical Error : Default Media Missing')
                        sys.exit(-1)
                    else:
                        with open('Media/default.mp4', 'rb') as media_file:
                            media_data = media_file.read()

                SocketTools.send(self.socket, media_data)

                while True:
                    message, message_type = SocketTools.receive(self.socket, timeout=None)
                    # print(message, message_type)
                    CommandInterpreter.interpret(message, self.socket)
            elif self.type == 'management':
                print('Manager Connected')
                with open('devices.json', 'r') as json_file:
                    devices = json.load(json_file)
                SocketTools.send(self.socket, devices)

                while True:
                    message, message_type = SocketTools.receive(self.socket, timeout=None)
                    print(message, message_type)
                    CommandInterpreter.interpret(message, self.socket)

        except SocketTools.DisconnectError:
            print('[-] Killing Thread For (%s:%s)' % self.address)
            self.socket.shutdown(2)
            self.socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 12345))
server_socket.listen(5)
server_socket.settimeout(None)

with open('data.json', 'r') as json_file:
    try:
        data = json.load(json_file)
    except json.decoder.JSONDecodeError:
        data = {}
CommandInterpreter.set_data(data)

while True:
    conn, address = server_socket.accept()
    client_thread = ClientThread(conn, address)
    client_thread.start()
