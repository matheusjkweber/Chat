"""Message
This code implements a message class.
"""
__author__ = "Matheus Jose Krumenauer Weber"
__email__ = "matheus.jk.weber@gmail.com"

class Message:

    def __init__(self, client, message, timesent):
        self.client = client
        self.message = message
        self.timesent = timesent

    """Initialize the message."""


    def __str__(self):
        return '({}, {}, {})'.format(self.timesent, self.client.nickname, self.message)
