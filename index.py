# Import the modules
import socket
import threading
import cryptography.fernet as fernet
import secrets
import json

# Generate a random salt for encryption and decryption
salt = secrets.token_bytes(16)

# Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the socket options to reuse the address and port
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to a port
server.bind(('0.0.0.0', 8080))

# Listen for incoming connections
server.listen()

# A function to generate a key for each client based on their password
def generate_key(password):
    # Use PBKDF2 to derive a key from the password and salt
    key = fernet.Fernet.generate_key_from_password(password, salt)
    # Return the key as a Fernet object
    return fernet.Fernet(key)

# A function to handle each client connection
def handle_client(client):
    # Receive the client's name and password as a JSON string
    data = client.recv(1024).decode()
    # Parse the JSON string into a dictionary
    data = json.loads(data)
    # Get the name and password from the dictionary
    name = data['name']
    password = data['password']
    print(f"{name} has joined the chat.")

    # Generate a key for the client based on their password
    cipher = generate_key(password)

    # Send a welcome message to the client
    client.send(cipher.encrypt(f"Welcome to the chat, {name}!".encode()))

    # A loop to receive and broadcast messages from the client
    while True:
        try:
            # Receive an encrypted message from the client
            message = client.recv(1024)

            # Decrypt the message using the key
            message = cipher.decrypt(message).decode()

            # Print the message on the server console
            print(f"{name}: {message}")

            # Broadcast the message to all other clients
            broadcast(f"{name}: {message}".encode(), client)

        except:
            # Handle any exceptions or errors
            print(f"{name} has left the chat.")
            break

    # Close the client connection
    client.close()

# A function to broadcast a message to all clients except the sender
def broadcast(message, sender):
    # Loop through all connected clients
    for client in clients:
        # If the client is not the sender, send the message to them
        if client != sender:
            try:
                # Get the cipher object for the client from the ciphers dictionary
                cipher = ciphers[client]
                # Encrypt the message using the cipher object
                message = cipher.encrypt(message)
                # Send the encrypted message to the client
                client.send(message)
            except:
                # Handle any exceptions or errors
                print(f"Failed to send message to {client}.")
                continue

# A list to store all connected clients
clients = []

# A dictionary to store the cipher objects for each client
ciphers = {}

# A loop to accept new connections
while True:
    # Accept a new connection
    client, address = server.accept()

    # Add the client to the list of clients
    clients.append(client)

    # Start a new thread to handle the client connection
    thread = threading.Thread(target=handle_client, args=(client,))
    thread.start()
