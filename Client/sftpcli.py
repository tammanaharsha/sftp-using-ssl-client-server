import socket, sys, ssl, os

# Function to connect to the server
def connect_to_server(host, port, max_retries=50):
    num_retries = 0
    while num_retries < max_retries:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            conn = context.wrap_socket(client_socket, server_hostname=host)
            print(f'Connected to server at {host}:{port}')
            return conn
        except Exception as e:
            num_retries += 1
            print(f'Could not connect to the server. Retrying in 5 seconds ({num_retries}/{max_retries})...')
            print(f'Error message: {e}')
            time.sleep(5)
    print(f'Could not connect to the server after {max_retries} retries. Exiting...')
    sys.exit()

# Function to send credentials to the server

def send_credentials(conn, max_attempts=50):
    num_attempts = 0
    while num_attempts < max_attempts:
        username = input('Username: ')
        password = input('Password: ')
        conn.sendall(username.encode('utf-8'))
        conn.sendall(password.encode('utf-8'))
        response = conn.recv(1024).decode('utf-8')
        print(response)
        if response.startswith('Incorrect'):
            num_attempts += 1
            print('Invalid username or password:Try Again' )
            #print(f'Invalid username or password: {response} ({num_attempts}/{max_attempts})')
        else:
            print('Logged in successfully')
            return 0
    print(f'Exceeded maximum login attempts ({max_attempts}). Exiting...')
    sys.exit()


# Function to send a command to the server
def send_command(conn, command):
    conn.sendall(command.encode('utf-8'))
    response = conn.recv(1024).decode('utf-8')
    return response

# Function to send a file to the server
def send_file(conn, command):
    conn.sendall(command.encode('utf-8'))
    filepath = command.split()[1]
    try:
        with open(filepath, "rb") as filetosend:
            data = filetosend.read(1024)
            print('Sending file...')
            while data:
                conn.send(data)
                data = filetosend.read(1024)
    except Exception as e:
        print(f'Could not open file at the specified path {filepath}')
        print(f'Error message: {e}')
        return
    conn.send(b"Terminate")
    print("File sent successfully.")
    # print(conn.recv(1024).decode('utf-8'))

# Main function to run the client
def run_client():
    
    if len(sys.argv) < 3:
        print('Usage: python client.py <server_ip> <server_port>')
        sys.exit()
    # Get the server IP address and port number from the user input
    host = socket.gethostbyname(sys.argv[1])
    port = int(sys.argv[2])
    # Connect to the server
    conn = connect_to_server(host, port)
    # Send the client's credentials to the server
    login_response = send_credentials(conn)
    
    while login_response != 0:
        login_response = send_credentials(conn)
    # Wait for user input for sending commands
    while True:
        #print("inside while2")
        command = input('sftp > ').strip()
        if command.startswith('put'):
            send_file(conn, command)
        elif command == 'lls':
            print('\n'.join(os.listdir(os.getcwd())))
        elif command == 'exit':
            send_command(conn, command)
            # conn.recv(1024).decode('utf-8')
            conn.close()
            break
        else:
            print('Invalid command')

# Run the client
run_client()
