
import tkinter as ttk
import socket
import time

DEVICE_ID = 'manager-0001'


class Client:
    def __init__(self):
        self.id = ''
        self.name = ''
        self.location = ''
        self.timetable = []
        self.media_name = ''
        self.media_extension = ''
        self.media_last_update = ''

        self.online = False
        self.ip = ''


host = socket.gethostname()
ip = socket.gethostbyname(host)
port = 2004
buffer_size = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        client.connect((host, port))
        break
    except ConnectionRefusedError:
        print('[E] Server is Inaccessible, Attempting Again in 10s')
        time.sleep(10)

while True:
    data = client.recv(1024).decode()
    if 'REQUEST id' in data:
        client.send(DEVICE_ID.encode())
        wait_response = client.recv(1024).decode()
        print(wait_response)
        break

client.send('REQUEST CLIENT name;'.encode())
name = client.recv(1024).decode()
print(name)

client.send('REQUEST CLIENT media_extension;'.encode())
media_extension = client.recv(1024).decode()
print(media_extension)

client.send('REQUEST CLIENT media_last_update;'.encode())
media_last_update = client.recv(1024).decode()
print(media_last_update)

client.send('SET CLIENT client-0001 name TO name2;'.encode())
media_last_update = client.recv(1024).decode()
print(media_last_update)

# Tkinter Section

def update_media():
    client.send('COMMAND update media;'.encode())

def get_media():
    client.send('REQUEST media list;'.encode())
    data = client.recv(1024).decode()
    media = data[10:-1].split(', ')
    print('%s%s' % (data[:9], media))
    return media

media = get_media()

root = ttk.Tk()
root.title("Tk dropdown example")

# Add a grid
mainframe = ttk.Frame(root)
mainframe.grid(column=0,row=0, sticky=(ttk.N, ttk.W, ttk.E, ttk.S))
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)
mainframe.pack(pady = 100, padx = 100)

# Create a Tkinter variable
tkvar = ttk.StringVar(root)

tkvar.set(media[0]) # set the default option
popupMenu = ttk.OptionMenu(mainframe, tkvar, *media)
ttk.Label(mainframe, text="Choose Media").grid(row = 1, column = 1)
popupMenu.grid(row=2, column=1)

# on change dropdown value
def change_dropdown(*args):
    print( tkvar.get() )

button = ttk.Button(mainframe, text='Update Media (Server)', command=update_media)
button.grid(row = 3, column=1)

button2 = ttk.Button(mainframe, text='Update Media (This Client)', command=get_media)
button2.grid(row = 4, column=1)

# link function to change dropdown
tkvar.trace('w', change_dropdown)

root.mainloop()

client.detach()
client.close()