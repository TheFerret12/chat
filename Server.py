import socket
import select
"""Chat server to host users from all other IP addresses (0.0.0.0),
The server requires a password to connect, and a registration/log in process"""

host_all = '0.0.0.0'
port = 44444

#  Initializing server socket:
server = socket.socket()
server.bind((host_all, port))
server.listen()
print(f'Server is listening on port {port}')
#  Initializing users info:
registered_users_info = {'Admin':'$tr0ngPa$$w0rd'}  # Registered users info
sockets = [server]  # sockets list
online_users = ['Admin']  # online users
server_password = '123456'  # server password

def handle_new_connection(client):
    """Function that handles incoming connections to the server.
    activated when the server socket is ready to read"""
    while True:  # Authentication loop
        try:  # try block to handle client disconnecting during the authentication process
            client.send('Enter the server password to connect to the chat room:\npassword:'.encode())
            serv_pass = client.recv(1024).decode()
            if serv_pass != server_password:  # if server password is incorrect
                client.send('Wrong password'.encode())
                print('Wrong password login attempt')
                continue  # Restart authentication
            else: # if server password correct
                client.send('You have succesfully connected to the server!\n'
                            'Please enter your nickname:\n'.encode())
                nickname = client.recv(1024).decode()  # Receive nickname for identification

                if nickname in online_users:
                    client.send(f'Nickname {nickname} is already taken'.encode())
                    continue
                elif nickname in registered_users_info:  # if the nickname exists in registered users
                    client.send(f'--------login for user {nickname}--------\n'
                                f'password:\n'.encode())  # Start login
                    password = client.recv(1024).decode().strip()  # receive password
                    if password == registered_users_info[nickname]:  # if password matches nickname
                        return nickname  # return the nickname to the mainloop function
                    else:  # if password is incorrect
                        client.send('Wrong password'.encode())
                        continue  # Restart authentication
                else:  # if the chosen nickname is not in any of the lists
                    while True:  # Begin registration loop
                        try:  # require password twice and compare them:
                            client.send(f'-----Registration for {nickname}------\n'
                                        f'please select a password:\n'.encode())
                            pass1 = client.recv(1024).decode().strip()
                            client.send('Please re-enter your password:\n'.encode())
                            pass2 = client.recv(1024).decode().strip()
                            if pass1 == pass2:  # if passwords match
                                client.send(f'User "{nickname}" succesfully registered.'.encode())
                                registered_users_info[nickname] = pass1
                                return nickname  # return the nickname to the mainloop function

                            else:  # if passwords don't match
                                client.send('Passwords do not match.\n'.encode())  # registration loop restarts
                        except:
                            client.close()
                            print(f'error during client identification.\nclient: {client}')
        except ValueError as err:
            client.close()
            print(f'error while registering {client}\nError: {err}')
            return None  # if an error occurs during authentication




def send_msg(nickname, msg):
    """Function for broadcasting a sent message"""
    for sock in sockets[1:]:  # for all sockets excluding the server
        try:  # handle error while sending a message to client
            sock.send(f'<{nickname}>:{msg}'.encode())
        except:  # if sending the message failed, assume the client has disconnected
            print(f'Error sending message from socket: {sock}, user: {nickname}')
            sock.close()  # close the client's sock
            sockets.remove(sock)  # remove from sockets list
            online_users.remove(nickname)  # remove from online users

def main_loop():
    """Endless while loop that acts as the main function"""
    print('Mainloop started...')
    while True:  # starting an endless loop that will run as long as the server is up
        # read from sockets when a socket is either ready to read, or has raised an error
        read, write, err = select.select(sockets,[],sockets)
        for sock in read:  # iterate over sockets ready to read
            if sock == server:  # is the socket ready to read is the server - assume an incoming connection
                try:
                    client, addr = server.accept()
                    print(f'Connected with {client}, {addr}')  # log client's entry
                    client.send(f'Hello and welcome to the chatroom!\n'
                                f'There are {len(online_users)} users online\n'.encode())  # welcome
                    nickname = handle_new_connection(client)
                    # the nickname is the output returned from handle_connection
                    if nickname:  # if the handle_connection function returned a nickname, authentication was successful
                        sockets.append(client)  # add socket to sockets list
                        online_users.append(nickname)  # add nickname to online users
                        client.send('log in succesful\n'.encode())  # inform user they are logged in
                        # using the send_msg function, informing all other users that the user has joined the chat
                        send_msg('Admin', f'{nickname} has joined the chat!\n')
                    else:
                        raise Exception
                except:  # if an error occured during registration
                    print(f'Disconnecting from socket')  # log incident
                    print('User login/registration failure')
                    client.close()  # assume user has disconnected
            else:  # if the socket ready to read is not the server, assume a client has sent a message
                try:
                    incoming_msg = sock.recv(1024).decode()
                    if incoming_msg:
                        # if an incoming msg is received - pass the index position of user's nickname, and the message
                        # to the send_msg function
                        send_msg(f'{online_users[sockets.index(sock)]}', incoming_msg)
                    else:  # if there is no message - raise an error
                        raise Exception
                except:  # if an error occured, disconnect from socket
                    print(f'Disconnecting from {sock}')
                    sockets.remove(sock)
                    online_users.remove(nickname)
                    send_msg('Admin', f'{nickname} has left the chat!')
                    client.close()

        for error_socket in err:  # any socket that raises an error is closed
            error_socket.close()
main_loop()

#server.close()