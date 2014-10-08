# ----------------------------------------------------------------------------
# Filename:     model.py
# Author:       Harrison Hubbell
# Date:         10/07/2014
# Description:  Statistical modeling package for the Smartkeg
# ----------------------------------------------------------------------------

from socket_server import SmartkegSocketServer
from process import ChildProcess
import json

class Model(ChildProcess):
    def __init__(self, pipe):
        super(Model, self).__init__(pipe)
        self.server = SmartkegSocketServer('', 8000)

    def main(self):
        while True:
            self.server.set_response(json.dumps({'name': 'Harry', 'age': 21, 'gender': 'Male'}))
            self.server.respond()

