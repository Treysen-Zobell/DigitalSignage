
import socket
import json
import ast
import sys

# Header = length + ':' + type + ':' + message
# Types = { 0:bytes, 1:str, 2:int, 3:float, 4:complex, 5:tuple, 6:dict, 7:bool }

error_buffer_size = 10
error_buffer = []

# WARNING WILL CONSUME MUCH RAM IF SENDING FILES
event_buffer_size = 0
event_buffer = []

disconnect_message = 'BYMZagRN7Y6w5A0FzQg3pDJe5BkY9MIX9ym8B'


class DisconnectError(Exception):
    pass


def send(conn, message, should_exit=False):
    try:
        # Convert message to bytes for transmission and get type
        if type(message) == bytes:
            message_type = b'0'

        elif type(message) == str:
            message = message.encode()
            message_type = b'1'

        elif type(message) == int:
            message = str(message).encode()
            message_type = b'2'

        elif type(message) == float:
            message = str(message).encode()
            message_type = b'3'

        elif type(message) == complex:
            message = str(message).encode()
            message_type = b'4'

        elif type(message) == tuple:
            message = str(message).encode()
            message_type = b'5'

        elif type(message) == dict:
            message = json.dumps(message).encode()
            message_type = b'6'

        elif type(message) == bool:
            message = str(message).encode()
            message_type = b'7'

        else:
            log_error(('TypeError', message))
            if should_exit:
                sys.exit(-1)
            return False

        length = str(len(message)).encode()
        delimiter = ':'.encode()
        transmission = length + delimiter + message_type + delimiter + message

        conn.sendall(transmission)
        log_event(('sent ', transmission))

        return True

    except socket.error as e:
        log_error(e)
        log_event(('error', e))
        if should_exit:
            sys.exit(-1)
        raise DisconnectError


def receive(conn, timeout=5, should_exit=False):
    try:
        conn.settimeout(timeout)  # Set socket timeout, default=5

        # Retrieve message length from buffer
        message_length = conn.recv(1).decode()
        while ':' not in message_length:
            data = conn.recv(1).decode()
            if not data:
                log_error('client disconnected')
                log_event(('error', 'client_disconnected'))
                if should_exit:
                    sys.exit(-1)
            else:
                message_length += data

        message_length = int(message_length[:-1])

        # Retrieve type from buffer
        message_type = conn.recv(1).decode()
        while ':' not in message_type:
            data = conn.recv(1).decode()
            if not data:
                log_error('client disconnected')
                log_event(('error', 'client_disconnected'))
                if should_exit:
                    sys.exit(-1)
            else:
                message_type += data
        message_type = message_type[:-1]

        # Retrieve message from buffer
        message = conn.recv(message_length)
        while len(message) < message_length:
            data = conn.recv(message_length - len(message))
            if not data:
                log_error('client disconnected')
                log_event(('error', 'client_disconnected'))
                if should_exit:
                    sys.exit(-1)
            else:
                message += data

        if message_type == '0':
            log_event(('received', bytes, message))
            return message, bytes

        elif message_type == '1':
            log_event(('received', str, message))
            message = message.decode()
            if message == disconnect_message:
                log_error('disconnect')
                raise DisconnectError
            return message, str

        elif message_type == '2':
            log_event(('received', int, message))
            return int(message.decode()), int

        elif message_type == '3':
            log_event(('received', float, message))
            return float(message.decode()), float

        elif message_type == '4':
            log_event(('received', complex, message))
            return complex(message.decode()), complex

        elif message_type == '5':
            log_event(('received', tuple, message))
            return ast.literal_eval(message.decode()), tuple

        elif message_type == '6':
            log_event(('received', dict, message))
            return json.loads(message.decode()), dict

        elif message_type == '7':
            log_event(('received', bool, message))
            return 'True' in message.decode(), bool

    except socket.error as e:
        log_error(e)
        log_event(('error', e))
        if should_exit:
            sys.exit(-1)
        else:
            raise DisconnectError


def log_error(e):
    global error_buffer, error_buffer_size
    error_buffer.insert(0, e)
    if error_buffer_size == 0:
        error_buffer = []
    elif len(error_buffer) > error_buffer_size:
        error_buffer = error_buffer[:error_buffer_size - 1]


def get_last_error():
    global error_buffer
    if error_buffer:
        return error_buffer[0]
    else:
        return None


def get_errors():
    global error_buffer
    return error_buffer


def log_event(e):
    global event_buffer, event_buffer_size
    event_buffer.insert(0, e)
    if event_buffer_size == 0:
        event_buffer = []
    elif len(event_buffer) > event_buffer_size:
        event_buffer = event_buffer[:event_buffer_size - 1]


def get_last_event():
    global event_buffer
    if event_buffer:
        return event_buffer[0]
    else:
        return None


def get_events():
    global event_buffer
    return event_buffer


def disconnect(conn):
    send(conn, disconnect_message)
    conn.shutdown(2)
    conn.close()
