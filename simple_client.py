
import socket
import time

buffer_size = 1024
server_ip = '127.0.0.1'
port = 2004

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Declare Connection Type (IPv4, Stream)

# Attempt to Connect Every 5 Seconds Until Connection Is Established
while True:
    try:
        connection.connect((server_ip, port))  # Try to Connect to Server Ip on Port
        break  # Break Loop
    except ConnectionRefusedError:
        print('[E] Server is Inaccessible, Attempting Again in 5s')  # Show Connection Refused On Console
        time.sleep(5)  # Delay For 5 Seconds

connection.send(str(0).encode())  # Start Handshake With a 0

# Pass Number Back and Forth Until It Exceeds 1000
while True:
    num = int(connection.recv(buffer_size).decode())  # Receive Number From Server
    num += 1  # Increment By 1
    connection.send(str(num).encode())  # Convert Number to String Equivalent, Encode, and Send
    print('num = %i' % num)  # Display Current Number On Console
    if num > 1000:  # Check if Number Exceeds 1000
        break  # If Number Is Greater Than 1000 Break Loop
