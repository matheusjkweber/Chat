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

test1 = server.login("Test", "100.000.000.00")

test2 = server.login("Test 1", "100.000.000.00")

test3 = server.login("Test 2", "100.000.000.00")

admin = Client("admin", True, "100.000.000.00")

is_created = server.create_room(admin, "Room 1")

#is_deleted = server.delete_room(admin, "Room 1")



server.enter_room(test1, "Room 1")

server.enter_room(test2, "Room 1")

server.enter_room(test3, "Room 1")

server.leave_room(test2, "Room 1")

message = Message(test1, "Message test", datetime.now)

server.send_message_to_room(message, test1, "Room 1")

server.send_message_to_room(message, test2, "Room 1")

print(jsonpickle.encode(server.rooms[0]));


#print(server.send_private_message(message, test1, "Test"))

#print(server.clients[0].messages)
#print(server.rooms[0].messages)
