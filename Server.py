"""Server
This code implements a server class.
"""
__author__ = "Matheus Jose Krumenauer Weber"
__email__ = "matheus.jk.weber@gmail.com"

from Client import Client
from Token import Token
from Room import Room

from datetime import datetime

class Server:

    def __init__(self):
        self.clients = []
        self.messages = []
        self.rooms = []

    """Intialize the server."""

    def login(self, nickname, ip):
        if self.verify_nickname(nickname):
            client = Client(nickname, False, ip)
            token = Token(len(self.clients))
            client.token = token
            self.clients.append(client)

            """TODO: Send client to user."""
            return client
        else:
            return "Nickname already used."

    """Login the user or return a error."""

    def verify_nickname(self, nickname):
        for client in self.clients:
            if client.nickname == nickname:
                return False

        return True

    """Verify if exists the nickname."""

    def send_rooms(self, client):
        """TODO: Send rooms to client."""
        pass

    """Send the rooms to client."""

    def create_room(self, client, name):
        if client.is_admin == True:
            for room in self.rooms:
                if room.name == name:
                    return "Already have a room with this name."
            room = Room(name)
            self.rooms.append(room)
            return True
        return "You don`t have the permission to create a room."

    """Create room."""

    def delete_room(self, client, name):
        if client.is_admin == True:
            removed = False
            for room in self.rooms:
                if room.name == name:
                    self.rooms.remove(room)
                    removed = True
                    return True

            if removed == False:
                return "Room not found in the server."
        return "You don`t have the permission to remove a room."

    """Remove room."""

    def verify_token(self, client):
        for c in self.clients:
            if c.nickname == client.nickname and c.token.active == True:
                return True

        return False

    def renew_token(self, client):
        for c in self.clients:
            if c == client:
                if c.get_new_token(client.renew_token):
                    return c

        return False

    """Renew the client token."""

    def enter_room(self, client, room_name):
        if self.verify_token(client):
            for room in self.rooms:
                if room.name == room_name:
                    room.clients.append(client)
                    """Send a warning to everybody showing when enter the room."""
                    return True
                    """Send the room to the client and all clients in the room."""
            return "Room not found in the server."
        else:
            return "Token expired."

    """Enter in room."""

    def leave_room(self, client, room_name):
        for room in self.rooms:
            if room.name == room_name:
                for c in room.clients:
                    if c.nickname == client.nickname:
                        room.clients.remove(c)
                        """Send a warning to everybody showing when leave the room."""
                        return True
                """Send the room to the client and all clients in the room."""
                return "Client not found in the room."
        return "Room not found in the server."

    """Leave room."""

    def send_message_to_room(self, message, client, room_name):
        if self.verify_token(client):
            for room in self.rooms:
                if room.name == room_name:
                    room.messages.append(message)
                    return True
                    """Send the room to the client and all clients in the room."""
            return "Room not found in the server."
        else:
            return "Token expired."

    """Send a message to the room."""

    def send_private_message(self, message, client, nickname):
        if self.verify_token(client):
            for c in self.clients:
                if c.nickname == nickname:
                    c.messages.append(message)
                    return True
                    """Send message to the client."""
            return "Client not found in the server."
        else:
            return "Token expired."

    """Send a private message to a client."""

    def send_clients(self, room_name):
        # Send a list with all clients in the room.
        pass

