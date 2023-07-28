
# Import the necessary modules

import socketio

import eventlet

import cryptography.fernet

# Create a socketio server object

sio = socketio.Server()

# Create a web server object

app = eventlet.wsgi.app

# Generate a secret key for encryption and decryption

key = cryptography.fernet.Fernet.generate_key()

f = cryptography.fernet.Fernet(key)

# A function to handle the connection event

@sio.event

def connect(sid, environ):

    # Send the secret key to the client

    sio.emit('key', key, room=sid)

    # Print a message to the console

    print(f'Client {sid} has connected.')

# A function to handle the message event

@sio.event

def message(sid, data):

    # Decrypt the message using the secret key

    message = f.decrypt(data).decode()

    # Print the message to the console

    print(f'Client {sid}: {message}')

    # Broadcast the message to all other clients

    sio.emit('message', data, skip_sid=sid)

# A function to handle the disconnect event

@sio.event

def disconnect(sid):

    # Print a message to the console

    print(f'Client {sid} has disconnected.')

# Run the web server on port 8080

if __name__ == '__main__':

    print('Server is running on port 8080.')

    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
