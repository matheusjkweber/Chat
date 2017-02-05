"""Room
This code implements a room class.
"""
__author__ = "Matheus Jose Krumenauer Weber"
__email__ = "matheus.jk.weber@gmail.com"

class Room:

    def __init__(self, name):
        self.name = name
        self.clients = []
        self.messages = []
        self.active = 1

    """Initialize the room."""

    def send_message(self, message):
        self.append(message)

    """Send a message to the room."""

