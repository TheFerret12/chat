import socket
import threading

"""Basic client for connecting to the chat server"""

host = '127.0.0.1'  # default
port = 44444

client = socket.socket()  # initialize the client socket
connected = False  # Initialize a bool variable to stop threads when disconnected


def read_msg(client):
    """Function for receiving a message from the server, and printing it to the user"""
    global connected
    while connected:
        try:  # handle error while receiving message
            msg = client.recv(1024).decode()
            if msg:  # if a message is received
                print(msg)
        except ValueError as e:  # if the read_msg function fails, assume server is down
            print(f'Error while receiving a message from the server.\nError: {e}')
            connected = False  # stop all other loops


def write_msg(client):
    """Function for sending a message input by the user"""
    global connected
    while connected:
        try:
            message = input('')
            if message == 'Exit':  # if the user sends "Exit"
                connected = False
                print('Goodbye!')
                exit()
            else:  # any other message is sent to the server
                client.send(message.encode())
        except ValueError as e:  # if the write_msg function fails, assume server is down
            print(f'Error while sending a message to the server\n Error: {e}')
            connected = False
            break


def mainloop():
    """Initial connection to the server"""
    global connected
    try:  # try connecting
        client.connect((host,port))
        connected = True
        print(f'connected to server on {host}:{port}\n'
              f'Enter "Exit" at any time to leave the chat!')
    except ValueError as e:  # if connection fails assume server is down - close the socket
        print(f'Error while trying to connect to server.\nError: {e}')
        connected = False
        client.close()

    read_thread = threading.Thread(target=read_msg, args=(client,))  # thread that handles the read_msg function
    read_thread.start()

    write_msg(client)  # main thread handles the write_msg function


mainloop()

