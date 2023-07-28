# Import the necessary modules
import socket
import threading
import cryptography.fernet

# Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a port
server.bind(('0.0.0.0', 8080))

# Listen for incoming connections
server.listen()

# Generate a secret key for encryption and decryption
key = cryptography.fernet.Fernet.generate_key()
f = cryptography.fernet.Fernet(key)

# A function to handle each client connection
def handle_client(client):
    # Receive the client's name
    name = client.recv(1024).decode()
    # Send the secret key to the client
    client.send(key)
    # Print a message to the console
    print(f'{name} has joined the chat.')
    # Loop to receive and send messages
    while True:
        try:
            # Receive an encrypted message from the client
            message = client.recv(1024)
            # Decrypt the message using the secret key
            message = f.decrypt(message).decode()
            # Print the message to the console
            print(f'{name}: {message}')
            # Broadcast the message to all other clients
            broadcast(f'{name}: {message}'.encode())
        except:
            # Print a message to the console if an error occurs
            print(f'{name} has left the chat.')
            # Remove the client from the list of clients
            clients.remove(client)
            # Close the connection
            client.close()
            # Break out of the loop
            break

# A function to broadcast a message to all clients
def broadcast(message):
    # Encrypt the message using the secret key
    message = f.encrypt(message)
    # Loop through all clients in the list of clients
    for client in clients:
        # Send the encrypted message to each client
        client.send(message)

# A list to store all connected clients
clients = []

# A loop to accept new connections
while True:
    # Accept a connection from a client
    client, address = server.accept()
    # Add the client to the list of clients
    clients.append(client)
    # Start a new thread to handle the client connection
    thread = threading.Thread(target=handle_client, args=(client,))
    thread.start()
