
import threading
import socket

buffer_size = 1024


# Client Threads Are Unique to Each Client, Each Contains The Connection
class ClientThread(threading.Thread):
    def __init__(self, connection):
        print('[+] Starting Thread (%s:%s)' % connection.getsockname())
        threading.Thread.__init__(self)

        self.connection = connection

    def run(self):
        while True:
            num = int(self.connection.recv(buffer_size).decode())
            num += 1
            self.connection.send(str(num).encode())
            print('num = %i' % num)
            if num > 1000:
                break

        print('[-] Killing Thread (%s:%s)' % self.connection.getsockname())


tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((socket.gethostname(), 2004))

while True:
    tcp_server.listen(50)
    client_connection, (ip, port) = tcp_server.accept()
    client_thread = ClientThread(client_connection)
    client_thread.start()
