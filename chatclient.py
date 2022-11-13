import socket
import select
import errno

HEADER_LENGTH = 10

HOST = "127.0.0.1"
PORT = 1234
my_username = input("Please enter your Username: ")

# Create a socket
# socket.AF_INET, state address family, IPv4
# socket.SOCK_STREAM, state TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to defined HOST address and PORT number
client_socket.connect((HOST, PORT))

# Set socket connection to non-blocking(false) state to prevent .recv() call from blocking, returns excception
client_socket.setblocking(False)

# Encode username via utf-8 encoding, encode inputted string(s) into bytes, then count # of bytes and prep header of defined length = 10, encode
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

while True:

    # Prompt in console for user to input their message
    message = input(f'{my_username} > ')

    # If message contains strings, send message
    if message:

        # Encode message and header to bytes(utf-8 encoding), prep header (username), then send
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)

    try:
        # while True, loop all non-empty messages recieved and print 
        while True:

            # Receive our "header" containing username length, it's size is defined and constant
            username_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            # Convert header to int value
            username_length = int(username_header.decode('utf-8').strip())

            # Decode username from bytes(utf-8) into strings
            username = client_socket.recv(username_length).decode('utf-8')

            # Decode message form bytes(utf-8) into strings, header length is not checked
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            # Print 'username: message'
            print(f'{username} > {message}')

    except IOError as e:
        # No incoming data = error
        # Check for no incoming data, if expected, means no incoming data, continue 
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # no errors recieved = continue
        continue

    except Exception as e:
        # Any exceptions occur, exit program
        print('Reading error: '.format(str(e)))
        sys.exit()