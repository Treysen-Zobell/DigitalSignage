
from SocketTools import SocketTools

import json
import os

data = {}


def interpret(command, connection, send=True):
    global data
    try:
        command_segments = command.split(' ')

        if command_segments[0] == 'set':
            data[command_segments[1]] = ' '.join(command_segments[2:])
            return True

        elif command_segments[0] == 'get':
            try:
                if send:
                    SocketTools.send(connection, data[command_segments[1]])
                else:
                    data[command_segments[1]]
                return True
            except KeyError:
                if send:
                    SocketTools.send(connection, 'KeyError')
                return False

        elif command_segments[0] == 'delete':
            try:
                del data[command_segments[1]]
                return True
            except KeyError:
                return False

        elif command_segments[0] == 'system':
            os.system(' '.join(command_segments[1:]))
            return True

        elif command_segments[0] == 'transfer':
            try:
                with open(command_segments[1], 'rb') as file:
                    file_data = file.read()
                if send:
                    SocketTools.send(connection, file_data)
                return True

            except FileNotFoundError:
                if send:
                    SocketTools.send(connection, 'FileNotFoundError')
                return False

        elif command_segments[0] == 'save':
            with open('data.json', 'w') as json_file:
                json.dump(data, json_file)

    except IndexError:
        if send:
            SocketTools.send(connection, 'invalid command')


def set_data(new_data):
    global data
    data = new_data
