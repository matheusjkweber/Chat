"""Client
This code implements a client class.
"""
__author__ = "Matheus Jose Krumenauer Weber"
__email__ = "matheus.jk.weber@gmail.com"

from datetime import datetime

class Client:

    def __init__(self, nickname, is_admin, ip):
        self.nickname = nickname
        self.is_admin = is_admin
        self.ip = ip
        self.is_online = True
        self.is_typing = False
        self.is_active = True
        self.last_activity = datetime.now()
        self.token = None
        self.messages = []
    """Initialize the client."""

    def update_activity(self):
        self.last_activity = datetime.now()

    """Update the last activity from client."""

    def send_message(self, message, senderId):
        self.messages[senderId].append(message)

    """Send a message to the user."""
