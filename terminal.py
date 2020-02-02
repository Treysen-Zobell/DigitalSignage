
from SocketTools import SocketTools

import socket
import time
import uuid


def connect(connection):
    SocketTools.send(connection, mac_address)
    media_data = SocketTools.receive(connection, timeout=None)[0]
    with open('Media/media.mp4', 'wb') as media_file:
        media_file.write(media_data)
    SocketTools.send(connection, 'get %s_timetable' % mac_address)
    cec_timetable = SocketTools.receive(connection)[0]
    return cec_timetable


try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(('127.0.0.1', 12345))
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])

    try:
        connect(server_socket)
        while True:
            message = input('Send: ')

            SocketTools.send(server_socket, message)
            if message.startswith('get'):
                print(SocketTools.receive(server_socket))

    except SocketTools.DisconnectError:
        pass

    SocketTools.disconnect(server_socket)

except SocketTools.DisconnectError:
    print('Disconnected.')
