"""Token
This code implements a token class.
"""
__author__ = "Matheus Jose Krumenauer Weber"
__email__ = "matheus.jk.weber@gmail.com"

from datetime import datetime, timedelta
from random import choice
from string import ascii_uppercase

class Token:

    def __init__(self, idClient):
        self.idClient = idClient
        self.token = ""
        self.active = False
        self.expire = ""
        self.renew_token = ""
        self.get_new_token(self.renew_token)

    """Initialize the token."""

    def get_new_token(self, renew_token):
        if self.renew_token == renew_token:
            # self.active = datetime.today() + timedelta(hours=1)
            self.renew_token = self.generate_token()
            self.token = self.generate_token()
            self.active = True
            return True
        return False

    """Renew the token."""

    def verify_token(self):
        # present = datetime.now()
        # if self.expire < present:
        #     self.active = False

        # return
        return True

    """Verify if the token is valid and return."""

    def generate_token(self):
        return (''.join(choice(ascii_uppercase) for i in range(12)))
