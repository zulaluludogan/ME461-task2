#!/usr/bin/env python3

import socket
from server_func import *

# Server IP is where the server python file will be running and accepting connections
server = "localhost" #"127.0.0.1"
# Port is where server will keep listening. Better to use a higher port as that is usually not used
port = 5555

# Initiate socket for the connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server and port with socket
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

# Start listening for client connections
s.listen()
print("Waiting for a connection, Server Started")

# Initialize the blank game queue
game_ids = []
# Start loop for accepting incoming connections from clients (i.e. players) to this server
while True:
    # Accept client connection
    conn, addr = s.accept()
    print("Connected to:", addr)

    # Get the game id and player id
    game_id, player_id = get_game_player_id()
    print("Game id -", game_id, ", Player id -", player_id)
    print('Game length -', len(game_ids))

    # Start new threaded connection with client and call the method to handle the thread.
    start_new_thread(threaded_client, (conn, game_id, player_id))
