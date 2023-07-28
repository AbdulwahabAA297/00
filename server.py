
import socket

import threading

import cryptography

from cryptography.fernet import Fernet

from cryptography.hazmat.primitives import hashes, serialization

from cryptography.hazmat.primitives.asymmetric import padding, rsa

from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

from cryptography.exceptions import InvalidSignature

from flask import Flask, render_template

# Generate a symmetric key for encryption and decryption

symmetric_key = Fernet.generate_key()

f = Fernet(symmetric_key)

# Generate a private and public key pair for authentication and digital signatures

private_key = rsa.generate_private_key(

    public_exponent=65537,

    key_size=2048,

)

public_key = private_key.public_key()

# Save the public key to a file

with open("public_key.pem", "wb") as f:

    f.write(public_key.public_bytes(

        encoding=serialization.Encoding.PEM,

        format=serialization.PublicFormat.SubjectPublicKeyInfo,

    ))

# Load the public key of the other user from a file

with open("other_public_key.pem", "rb") as f:

    other_public_key = load_pem_public_key(f.read())

# Create a socket object for the server

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the server to a port

host = "0.0.0.0"

port = 5000

server.bind((host, port))

# Listen for incoming connections

server.listen(5)

print(f"Server listening on {host}:{port}")

# Create a list of connected clients

clients = []

# Define a function to handle each client connection

def handle_client(client):

    # Receive the username of the client

    username = client.recv(1024).decode()

    print(f"{username} has joined the chat")

    # Send a welcome message to the client

    message = f"Welcome {username}! You are now connected to the most secure chatting python program ever."

    client.send(message.encode())

    # Send the symmetric key and the public key to the client

    client.send(symmetric_key)

    client.send(public_key.public_bytes(

        encoding=serialization.Encoding.PEM,

        format=serialization.PublicFormat.SubjectPublicKeyInfo,

    ))

    # Receive messages from the client and broadcast them to other clients

    while True:

        try:

            # Receive an encrypted and signed message from the client

            encrypted_message = client.recv(1024)

            signature = client.recv(256)

            # Verify the signature using the other public key

            other_public_key.verify(

                signature,

                encrypted_message,

                padding.PSS(

                    mgf=padding.MGF1(hashes.SHA256()),

                    salt_length=padding.PSS.MAX_LENGTH,

                ),

                hashes.SHA256(),

            )

            # Decrypt the message using the symmetric key

            decrypted_message = f.decrypt(encrypted_message).decode()

            # Print the message to the console

            print(f"{username}: {decrypted_message}")

            # Broadcast the message to other clients

            for c in clients:

                if c != client:

                    c.send(encrypted_message)

                    c.send(signature)

        except InvalidSignature:

            # If the signature is invalid, print an error message and close the connection

            print(f"Invalid signature from {username}")

            client.close()

            clients.remove(client)

            break

        except Exception as e:

            # If any other exception occurs, print an error message and close the connection

            print(f"Error: {e}")

            client.close()

            clients.remove(client)

            break

# Define a function to accept new client connections

def accept_clients():

    while True:

        # Accept a new connection from a client

        client, address = server.accept()

        print(f"New connection from {address}")

        # Add the client to the list of connected clients

        clients.append(client)

        # Start a new thread to handle the client connection

        thread = threading.Thread(target=handle_client, args=(client,))

        thread.start()

# Start a new thread to accept new client connections

thread = threading.Thread(target=accept_clients)

thread.start()

# Create a flask app for serving a webpage that shows if the server is running or not

app = Flask(__name__)

@app.route("/")

def index():

    return render_template("index.html", status="running")

# Run the flask app on the same port as the server

app.run(host=host, port=port)
