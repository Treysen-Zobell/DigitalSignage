
from SocketTools import SocketTools

import subprocess
import threading
import datetime
import platform
import socket
import time
import uuid
# import cec
import os


SERVER_IP = '192.168.1.8'
SERVER_PORT = 12345


class CECThread(threading.Thread):
    def __init__(self, cec_timetable):
        threading.Thread.__init__(self)
        # cec.init()
        # self.tv = cec.Device(cec.CECDEVICE_TV)
        self.timetable = self.load_timetable(cec_timetable)
        # self.tv.power_on()
        self.tv_is_on = True

    def run(self):
        now = datetime.datetime.now().time()
        if self.timetable[0] <= self.timetable[1]:
            should_be_on = self.timetable[0] <= now <= self.timetable[1]
        else:
            should_be_on = self.timetable[0] <= now or now <= self.timetable[1]

        if should_be_on:
            if not self.tv_is_on:
                print('Tv On Sent')  # self.tv.power_on()
                self.tv_is_on = True
        else:
            if self.tv_is_on:
                print('Tv Off Sent')  # self.tv.standby()
                self.tv_is_on = False

    @staticmethod
    def load_timetable(cec_timetable):
        cec_timetable = cec_timetable.split(',')
        start = cec_timetable[0].split(':')
        start = datetime.time(int(start[0]), int(start[1]))
        end = cec_timetable[1].split(':')
        end = datetime.time(int(end[0]), int(end[1]))
        return start, end


def connect(connection):
    SocketTools.send(connection, 'client')
    SocketTools.send(connection, mac_address)
    media_data = SocketTools.receive(connection, timeout=None)[0]
    with open('Media/media.mp4', 'wb+') as media_file:
        media_file.write(media_data)
    SocketTools.send(connection, 'get %s_timetable' % mac_address)
    cec_timetable = SocketTools.receive(connection)[0]
    return cec_timetable


def restart_media():
    system = platform.system()
    if system == 'Linux':
        os.system('killall vlc')
        os.system('cp Media/media.mp4.tmp Media/media.mp4')
        subprocess.Popen(['cvlc', '-f', '--loop', 'Media/media.mp4'])


try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((SERVER_IP, SERVER_PORT))
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
    print(mac_address)

    try:
        timetable = connect(server_socket)
        cec_thread = CECThread(timetable)
        cec_thread.start()
        while True:
            SocketTools.send(server_socket, 'get %s_should_update' % mac_address)
            should_update = 'True' in SocketTools.receive(server_socket)[0]

            if should_update:
                SocketTools.send(server_socket, 'get %s_media' % mac_address)
                media_name = SocketTools.receive(server_socket)[0]

                SocketTools.send(server_socket, 'transfer %s' % media_name)
                file_data = SocketTools.receive(server_socket, timeout=None)[0]
                with open('Media/media.mp4.tmp', 'wb+') as file:
                    file.write(file_data)

                SocketTools.send(server_socket, 'get %s_timetable' % mac_address)
                timetable = SocketTools.receive(server_socket)[0]
                timetable = cec_thread.load_timetable(timetable)
                cec_thread.timetable = timetable
                print(timetable)

                SocketTools.send(server_socket, 'set %s_should_update false' % mac_address)

                restart_media()

            else:
                print('Up to date')

            time.sleep(30)

    except SocketTools.DisconnectError:
        pass  # Replace with reconnect or reboot attempts

    SocketTools.disconnect(server_socket)

except SocketTools.DisconnectError:
    print('Disconnected.')
