"""ApiMessage
This code implements a apiMessage class.
"""
__author__ = "Matheus Jose Krumenauer Weber"
__email__ = "matheus.jk.weber@gmail.com"

import jsonpickle

class ApiMessage:
    def __init__(self, code, message, object):
        self.code = code
        self.message = message
        self.object = object

    def returnJson(self):
        dict = {"code": self.code, "message": self.message, "object": self.object}
        return jsonpickle.encode(dict)
