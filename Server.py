"""Server
This code implements a server class.
"""
__author__ = "Matheus Jose Krumenauer Weber"
__email__ = "matheus.jk.weber@gmail.com"

from Client import Client
from Token import Token
from Room import Room
from ApiMessage import ApiMessage
from Message import Message
import jsonpickle

from datetime import datetime

class Server:

    def __init__(self):
        self.clients = []
        self.messages = []
        self.rooms = []

    """Intialize the server."""

    def login(self, nickname, ip, debug = True):
        if self.verify_nickname(nickname):
            client = Client(nickname, False, ip)
            token = Token(len(self.clients))
            client.token = token
            self.clients.append(client)

            """TODO: Send client to user."""
            if debug == False:
                return ApiMessage(200, "", client).returnJson()
            return client
        else:
            return ApiMessage(404, "Nickname already used.", None).returnJson()

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

    def send_clients(self, room_name):
        # Send a list with all clients in the room.
        pass

    def get_users_online(self):
        clients = []
        for c in self.clients:
            clients.append(c.nickname);

        return ApiMessage(200, "", clients).returnJson();

    """Get the users online."""

    def get_private_messages(self, token):
        client = None
        for c in self.clients:
            if c.token == token:
                client = c

        if client != None:
            return ApiMessage(200, "", client.messages).returnJson()

        return ApiMessage(404, "No client found with this token.", None).returnJson()

    """Get private messages using token."""

    def send_private_message(self, token, nickname, message):
        sender = self.get_client_by_token(token)
        if self.verify_token(sender):
            target = self.get_client_by_nickname(nickname)
            if target != None:
                new_message = Message(sender, message, datetime.now())
                sender.messages.append(new_message)
                target.messages.append(new_message)
                return ApiMessage(200, "", None)
            else:
                return ApiMessage(404, "No client with this nickname found.", None).returnJson()

        else:
            return ApiMessage(404, "Token expired.", None).returnJson()

    """Send a private message to a client."""

    def get_client_by_token(self, token):
        for c in self.clients:
            if c.token == token:
                return c
        return None

    """Get client by token."""

    def get_client_by_nickname(self, nickname):
        for c in self.clients:
            if c.nickname == nickname:
                return c
        return None

    """Get client by name."""
