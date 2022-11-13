import socket, select

HEADER_LENGTH = 10

Host = "127.0.0.1"
PORT = 1234

# Create a socket with adress and TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind socket to host and port
server_socket.bind((Host, PORT))

# socket server will listen to new connections
server_socket.listen()

# List of sockets
sockets_list = [server_socket]

# List of connected clients
clients = {}

# print connection confirmation
print(f'Listening for connections on {Host}:{PORT}...')

# tracks messages recived 
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length
        message_header = client_socket.recv(HEADER_LENGTH)

        # Close conncetion if no data
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # connection is closed 
        return False

while True:

    # On call to wait for data 
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # loop for every notified sockets
    for notified_socket in read_sockets:

        # notified socket creates new socket
        if notified_socket == server_socket:

            # Accept new connection
            client_socket, client_address = server_socket.accept()

            # Clients username 
            user = receive_message(client_socket)

            # If False client is not connected 
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # save username and username header of new accepted socket
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        # existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # client disconnected if message not recived 
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove client from list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]
            # prints user information bytes format 
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # loop for connected clients and broadcast message
            for client_socket in clients:

                # But don't sent it to sender
                if client_socket != notified_socket:

                    # response send user and message
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                    