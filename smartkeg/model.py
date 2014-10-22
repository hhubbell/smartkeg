# ----------------------------------------------------------------------------
# Filename:     model.py
# Author:       Harrison Hubbell
# Date:         10/07/2014
# Description:  Statistical modeling package for the Smartkeg
# ----------------------------------------------------------------------------

from socket_server import SmartkegSocketServer
from process import ChildProcess
import time
import json

class Model(ChildProcess):
    def __init__(self, pipe):
        super(Model, self).__init__(pipe)
        self.server = SmartkegSocketServer('', 8000)

    def main(self):
        # This is an example of the JSON being sent.
        self.model = {
            'consumption': {
                'x': {
                    50: {
                        'y':[3, 5, 17, 23, 8, 6, 13, 14, 5, 16],
                        'mean': None,
                    },
                    150: {
                        'y':[6, 3, 7, 13, 16, 8, 16, 3, 4, 6],
                        'mean': None,
                    },
                    250: {
                        'y':[3, 8, 17, 9, 16, 8, 16, 13, 10, 6],
                        'mean': None,
                    },
                    350: {
                        'y':[9, 18, 56, 13, 6, 28, 16, 23, 24, 36],
                        'mean': None,
                    },
                    450: {
                        'y':[33, 43, 67, 53, 56, 48, 46, 33, 44, 36],
                        'mean': None,
                    },
                    550: {
                        'y':[93, 83, 77, 93, 96, 98, 116, 63, 64, 36],
                        'mean': None,
                    },
                    650: {
                        'y':[83, 83, 77, 93, 96, 98, 90, 43, 44, 46],
                        'mean': None,
                    }
                },
                'radius': 2,
                'style': 'circle'
            },
            'remaining': {
                'y': 94.13241234
            },
            'beer_info': {
                'brand': 'Fiddlehead',
                'name': 'Mastermind',
                'type': 'Ale',
                'subtype': 'Double IPA',
                'ABV': 8.2,
                'IBU': '???',
                'rating': 5
            }
        }
        self.server.set_response(json.dumps(self.model))

        while True:
            beer_data = self.proc_poll_recv()
            if beer_data:
                self.calculate_model(beer_data)
                self.server.set_response(json.dumps(self.model))
            
            self.server.respond()
            time.sleep(0.1)
