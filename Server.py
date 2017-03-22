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
import threading
# import jsonpickle
import json
import socket
import sys
import logging

from datetime import datetime

class Server:
    thread_names = []
    names = {}
    name_lock = threading.Lock()

    def __init__(self, port=10000):
        self.clients = []
        self.messages = []
        self.rooms = []
        self.port = port

        if Server.thread_names == []:
            f = open('thread_names', 'r')
            Server.thread_names = map(lambda name: name[:-1], f.readlines())
            f.close()

        self.listener_thread = threading.Thread(target=self.__listener)
        self.listener_thread.run()

    def __get_name(self):
        name = None
        with Server.name_lock:
            ident = threading.current_thread().ident
            if ident not in Server.names:
                Server.names[ident] = Server.thread_names.pop()
            name = Server.names[ident]
        return name

    def __listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen(5)

        while True:
            client, addr = s.accept()
            ct = threading.Thread(target=self.__client, args=(client,addr))
            ct.run()

    def __client(self, client, addr):
        try:
            me = self.__get_name()
            while True:
                request_raw = client.recv(4096)
                if len(request_raw) == 0:
                    print '[{}] closing socket for {}.'.format(me, addr)
                    client.close()
                    return
                try:
                    request = json.loads(request_raw)
                    response = ''
                    print '[{}] request from {}:{}'.format(me, addr, request_raw)
                    if 'execute' in request:
                        f = getattr(self, request['execute'], self.execute_invalid)
                        if f == self.execute_invalid:
                            response = self.execute_invalid(**request)
                        else:
                            try:
                                args = request.get('args', {})
                                args['ip'] = addr
                                response = f(**args)
                            except TypeError as e:
                                response = str(e)
                        print '[{}] respose to {}:{}'.format(me, addr, response)
                        client.send(response)
                except Exception as e:
                    print '[{}] ERROR on {}: {}'.format(me, request_raw, e)
                    raise
        except:
            raise

    def __ensure_args(self, function_name, **kwargs):
        for k, v in kwargs.items():
            if v == None:
                raise TypeError(ApiMessage(
                    404,
                    '{}: arguments \'{}\' must be valid.'.format(
                        function_name,
                        reduce(lambda a, b: '{}, {}'.format(a, b), kwargs.keys())),
                    None).returnJson())

    def execute_invalid(self, **kwargs):
        return ApiMessage(404, "invalid execution of {}".format(str(kwargs)), None).returnJson()

    """Intialize the server."""

    # Api Methods.
    def login(self, nickname=None, ip=None, **kwargs):
        self.__ensure_args('login', nickname=nickname)
        if self.verify_nickname(nickname):
            client = Client(nickname, ip)
            token = Token(len(self.clients))
            client.token = token
            self.clients.append(client)

            """TODO: Send client to user."""
            return ApiMessage(200, "", '({}, {})'.format(client, client.token.token)).returnJson()
        else:
            return ApiMessage(404, "Nickname already used.", None).returnJson()


    """Login the user or return a error."""

    def get_users_online(self, **kwargs):
        # clients = []
        # for c in self.clients:
        #     clients.append(c.nickname);
        clients = map(lambda c: c.nickname, self.clients)
        return ApiMessage(200, "", clients).returnJson();

    """Get the users online."""

    def get_private_messages(self, token=None, **kwargs):
        self.__ensure_args('get_private_messages',token=token)
        client = None
        for c in self.clients:
            if c.token == token:
                client = c
        if client != None:
            messages = [str(msg) for msg in client.messages]
            return ApiMessage(200, "", messages).returnJson()
        return ApiMessage(404, "No client found with this token.", None).returnJson()

    """Get private messages using token."""

    def send_private_message(self, token=None, nickname=None, message=None, **kwargs):
        self.__ensure_args('send_private_message',
            token=token, nickname=nickname, message=message)
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
            return ApiMessage(404, "Token expired 2.", None).returnJson()

    """Send a private message to a client."""

    def get_rooms(self, **kwargs):
        # rooms = []
        # for r in self.rooms:
        #     rooms.append(r.name);
        rooms = map(lambda r: r.name, self.rooms)
        return ApiMessage(200, "", rooms).returnJson();

    """Get rooms in the server."""

    def enter_room(self, token=None, room_name=None, **kwargs):
        self.__ensure_args('enter_room', token=token, room_name=room_name)
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
            return ApiMessage(404, "Token expired2 .", None).returnJson()

    """Enter in room."""

    def get_users_room(self, name=None, **kwargs):
        self.__ensure_args('get_users_room', name=name)
        room = self.get_room_by_name(name)
        clients = []
        if room != None:
            for c in room.clients:
                clients.append(c.nickname);
            return ApiMessage(200, "", clients).returnJson()
        return ApiMessage(404, "Room not found in the server.", None)

    """Get users in the room."""

    def get_messages_room(self, name=None, **kwargs):
        self.__ensure_args('get_messages_room', name=name)
        room = self.get_room_by_name(name)

        if room != None:
            messages = [str(msg) for msg in room.messages]
            return ApiMessage(200, "", messages).returnJson()

        return ApiMessage(404, "No room found with this name.", None).returnJson()

    """Get messages using room name."""

    def send_message_to_room(self, token=None, room_name=None, message=None, **kwargs):
        self.__ensure_args('send_message_to_room',
                           token=token, room_name=room_name, message=message)
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

    def leave_room(self, token=None, room_name=None, **kwargs):
        self.__ensure_args('leave_room', token=token, room_name=room_name)
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

    def logout(self, token=None, **kwargs):
        self.__ensure_args('logout', token=token)
        client = self.get_client_by_token(token)
        if client != None:
            if self.verify_token(client):
                for r in self.rooms:
                    self.leave_room(token, r.name)
                return ApiMessage(200, "", None).returnJson()
        return ApiMessage(404, "Token expired.", None).returnJson()

    # Server methods.
    """Create room."""
    def create_room(self, name=None, **kwargs):
        self.__ensure_args('create_room', name=name)
        for room in self.rooms:
            if room.name == name:
                return ApiMessage(404, "Already have a room with this name.", None).returnJson()
        room = Room(name)
        self.rooms.append(room)
        return  ApiMessage(200, "room created", None).returnJson()


    """Remove room."""
    def delete_room(self, name=None, **kwargs):
        self.__ensure_args('delete_room', name=name)
        for room in self.rooms:
            if room.name == name:
                self.rooms.remove(room)
            return  ApiMessage(200, "room deleted", None).returnJson()
        return ApiMessage(404, "Room not found in the server.", None).returnJson()

    # Auxiliar Methods.

    """Verify if exists the nickname."""
    def verify_nickname(self, nickname):
        for client in self.clients:
            if client.nickname == nickname:
                return False
        return True


    """Verify if the user token is valid"""
    def verify_token(self, client):
        # raise Exception()
        # print self.clients
        for c in self.clients:
            if c.nickname == client.nickname and c.token.active:
                # print json.dumps(c.token.__dict__)
                return True
        return False


    """Renew the client token."""
    def renew_token(self, client):
        for c in self.clients:
            if c == client:
                if c.get_new_token(client.renew_token):
                    return c

        return False


    """Get client by token."""
    def get_client_by_token(self, token):
        for c in self.clients:
            if c.token.token == token:
                return c
        return None


    """Get client by name."""
    def get_client_by_nickname(self, nickname):
        for c in self.clients:
            if c.nickname == nickname:
                return c
        return None


    """Get room by name."""
    def get_room_by_name(self, name):
        for r in self.rooms:
            if r.name == name:
                return r
        return None


if __name__ == '__main__':
    import random
    port = random.randrange(10000, 20000)
    print 'Serving at {}'.format(port)
    Server(port)
