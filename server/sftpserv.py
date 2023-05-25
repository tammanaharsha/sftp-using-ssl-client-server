import socket, os, sys, ssl

HOST = ''  # Server IP address
PORT = int(sys.argv[1])  # Server port number
PASSWORDS_FLPT = '../passwords.txt'

def main():
    users = load_users()
    server_socket = create_server_socket()
    print(f'Server is listening on {HOST}:{PORT}')

def main():
    users = load_users()
    server_socket = create_server_socket()
    client_socket, address = server_socket.accept()
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    ssl_socket = ssl_context.wrap_socket(client_socket, server_side=True)
    print(f'Connected with a client from {address}')

    # try:
    while True:
        # Accept incoming connections from clients and serve one client at a time
     
        conter=handle_client(ssl_socket, users)
        if conter==0:
            break
        
def load_users():
    with open(PASSWORDS_FLPT, "r") as file:
        users = {user: passw for user, passw in (line.strip().split() for line in file)}
    return users
        
'''def load_users():
    users = {}
    with open(PASSWORDS_FLPT, "r") as file:
        for line in file:
            user, passw = line.strip().split()
            users[user] = passw
    return users
'''
def create_server_socket():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen(1)
    print(f'Server is listening on {HOST}:{PORT}')
    return server_socket

def handle_client(ssl_socket, users):

    # Authentication loop
    authenticated = False
    while not authenticated:
        user_id = ssl_socket.recv(1024).decode('utf-8').strip()
        password = ssl_socket.recv(1024).decode('utf-8').strip()

        if authenticate_user(user_id, password, users):
            authenticated = True
            ssl_socket.sendall(b'Authentication is successful\n')
            print('Authentication successful for user: {}'.format(user_id))
        else:
            print('Authentication failed for user: {}'.format(user_id))
            ssl_socket.sendall(b'Incorrect ID or password\n')
            # ssl_socket.close()
            return 1

def handle_client(ssl_socket, users):

    user_id = ssl_socket.recv(1024).decode('utf-8').strip()
    password = ssl_socket.recv(1024).decode('utf-8').strip()

    if not authenticate_user(user_id, password, users):
        print('Authentication failed for user: {}'.format(user_id))
        ssl_socket.sendall(b'Incorrect ID or password\n')
        # ssl_socket.close()
        return 1
    
    ssl_socket.sendall(b'Authentication is successful\n')
    print('Authentication successful for user: {}'.format(user_id))

    # Receive commands from the client and execute them
    
    while True:
        check=1
        command = ssl_socket.recv(1024).decode('utf-8').strip()
        print(command)
        if command.startswith('put'):
            file_name = command.split()[1].split('/')[-1]
            with open(file_name, 'wb') as file:
                while True:
                    data = ssl_socket.recv(1024)
                    if data[-9:] == b'Terminate':
                        break
                    file.write(data)
            file.close()
            print('File "{}" received successfully'.format(file_name))
            ssl_socket.sendall(b'File received successfully\n')

        elif command == 'lls':
            # List all files and subdirectories in the current directory
            path = (os.getcwd())
            path = path[:len(path)-6] + 'client' 

        elif command == 'exit':
            # Close the connection
            check=0
            ssl_socket.shutdown(socket.SHUT_RDWR)
            ssl_socket.close()
            
            print('connection closed')
            break
        else:
            ssl_socket.sendall(b'Invalid command\n')
    
    return check

    print(f'Client disconnected')

def authenticate_user(user_id, password, users):
    if user_id in users and users[user_id] == password:
        return True
    return False

if __name__ == '__main__':
    main()
