"""Main
This code implements the main tests from server.
"""
__author__ = "Matheus Jose Krumenauer Weber"
__email__ = "matheus.jk.weber@gmail.com"

from Server import Server
from Client import Client
from Message import Message
from datetime import datetime
import jsonpickle

server = Server()
## Server test.

# Create rooms.
server.create_room("Room 1")
server.create_room("Room 2")
server.create_room("Room 3")
print(server.create_room("Room 3"))

# Remove room.
server.delete_room("Room 1")
print(server.delete_room("Room 1"))

print(server.rooms)
## Api Test

# Login clients to server.
print(server.login("Client 1", "111.222.333.444"))
print(server.login("Client 2", "111.222.333.444"))
print(server.login("Client 1", "111.222.333.444"))

# Return clients to client.
print(server.get_users_online())

# Return rooms to client.
print(server.get_rooms())

# Return private messages to client.
test_token = server.clients[0].token
test_token2 = server.clients[1].token

print(server.get_private_messages(test_token))
print(server.get_private_messages("assasa"))

# Client enter in a room.
print(server.enter_room(test_token, "Room 2"))
print(server.enter_room("sassasa", "Room 2"))
print(server.enter_room(test_token, "Room 4"))

print(server.enter_room(test_token2, "Room 2"))

# Return clients on room.
print(server.get_users_room("Room 2"))

# Client send message to a room.
print(server.send_message_to_room(test_token, "Room 2", "Test Message"))
print(server.send_message_to_room(test_token2, "Room 2", "Test Message 2"))
print(server.send_message_to_room("aaaa", "Room 2", "Error message"))
print(server.send_message_to_room(test_token, "Room 1", "Error message"))

print(server.rooms[0].messages)

# Return messages in the room to client.
print(server.get_messages_room("Room 2"))
print(server.get_messages_room("Room 1"))

# Client leave a room.
print(server.leave_room(test_token, "Room 2"))
print(server.leave_room("lalala", "Room 2"))
print(server.leave_room(test_token, "Room 1"))

print(server.rooms[0].clients)

# Client logout.
print(server.logout(test_token2))
print(server.clients)
print(server.rooms[0].clients)