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

    # Api Methods.
    def login(self, nickname, ip):
        if self.verify_nickname(nickname):
            client = Client(nickname, ip)
            token = Token(len(self.clients))
            client.token = token
            self.clients.append(client)

            """TODO: Send client to user."""
            return ApiMessage(200, "", client).returnJson()
        else:
            return ApiMessage(404, "Nickname already used.", None).returnJson()

    """Login the user or return a error."""

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
        if sender != None:
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
        else:
            return ApiMessage(404, "Token expired.", None).returnJson()

    """Send a private message to a client."""

    def get_rooms(self):
        rooms = []
        for r in self.rooms:
            rooms.append(r.name);

        return ApiMessage(200, "", rooms).returnJson();

    """Get rooms in the server."""

    def enter_room(self, token, room_name):
        sender = self.get_client_by_token(token)
        if sender != None:
            if self.verify_token(sender):
                for room in self.rooms:
                    if room.name == room_name:
                        room.clients.append(sender)
                        """Send a warning to everybody showing when enter the room."""
                        return ApiMessage(200, "", None).returnJson()
                        """Send the room to the client and all clients in the room."""
                return ApiMessage(404, "Room not found in the server.", None).returnJson()
            else:
                return ApiMessage(404, "Token expired.", None).returnJson()
        else:
            return ApiMessage(404, "Token expired.", None).returnJson()

    """Enter in room."""

    def get_users_room(self, name):
        room = self.get_room_by_name(name)
        clients = []
        if room != None:
            for c in room.clients:
                clients.append(c.nickname);

            return ApiMessage(200, "", clients).returnJson()
        return ApiMessage(404, "Room not found in the server.", None)

    """Get users in the room."""

    def get_messages_room(self, name):
        room = self.get_room_by_name(name)

        if room != None:
            return ApiMessage(200, "", room.messages).returnJson()

        return ApiMessage(404, "No room found with this name.", None).returnJson()

    """Get messages using room name."""

    def send_message_to_room(self, token, room_name, message):
        client = self.get_client_by_token(token)
        if client != None:
            if self.verify_token(client):
                room = self.get_room_by_name(room_name)
                if room != None:
                    msg = Message(client, message, datetime.now())
                    room.messages.append(msg)
                    return ApiMessage(200, "", None).returnJson()
                return ApiMessage(404, "No room found with this name.", None).returnJson()

        return ApiMessage(404, "Token expired.", None).returnJson()

    """Send a message to the room."""

    def leave_room(self, token, room_name):
        client = self.get_client_by_token(token)
        if client != None:
            if self.verify_token(client):
                room = self.get_room_by_name(room_name)
                if room != None:
                    for c in room.clients:
                        if c.token == token:
                            room.clients.remove(c)
                            return ApiMessage(200, "", None).returnJson()
                    return ApiMessage(404, "Client not found in this room", None).returnJson()
                return ApiMessage(404, "No room found with this name.", None).returnJson()
        return ApiMessage(404, "Token expired.", None).returnJson()

    """Leave room."""

    def logout(self, token):
        client = self.get_client_by_token(token)
        if client != None:
            if self.verify_token(client):
                for r in self.rooms:
                    self.leave_room(token, r.name)
                return ApiMessage(200, "", None).returnJson()
        return ApiMessage(404, "Token expired.", None).returnJson()

    # Server methods.
    def create_room(self, name):
        for room in self.rooms:
            if room.name == name:
                return "Already have a room with this name."
        room = Room(name)
        self.rooms.append(room)
        return True

    """Create room."""

    def delete_room(self, name):
        for room in self.rooms:
            if room.name == name:
                self.rooms.remove(room)
            return True

        return "Room not found in the server."

    """Remove room."""

    # Auxiliar Methods.

    def verify_nickname(self, nickname):
        for client in self.clients:
            if client.nickname == nickname:
                return False

        return True

    """Verify if exists the nickname."""

    def verify_token(self, client):
        for c in self.clients:
            if c.nickname == client.nickname and c.token.active == True:
                return True
        return False

    """Verify if the user token is valid"""

    def renew_token(self, client):
        for c in self.clients:
            if c == client:
                if c.get_new_token(client.renew_token):
                    return c

        return False

    """Renew the client token."""

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

    def get_room_by_name(self, name):
        for r in self.rooms:
            if r.name == name:
                return r
        return None

    """Get room by name."""