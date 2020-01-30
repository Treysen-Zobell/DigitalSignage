import subprocess
import threading
import socket
import time
import sys
import os

# Const Variables
SERVER_IP = socket.gethostname()
SERVER_PORT = 12345
BUFFER_SIZE = 1024
DEVICE_ID = '0001'


def send_request(connection, request):
    request = '%s;' % request
    connection.send(request.encode())


def get_reply(connection):
    reply = ''
    while ';' not in reply:
        reply += connection.recv(BUFFER_SIZE).decode()
    print(reply)
    reply = reply[:-1]
    return reply


server_connection = socket.socket()
server_connection.connect((SERVER_IP, SERVER_PORT))

while True:
    request = input('Request?: ')
    send_request(server_connection, request)
    get_reply(server_connection)
