# ----------------------------------------------------------------------------
# Filename:     model.py
# Author:       Harrison Hubbell
# Date:         10/07/2014
# Description:  Statistical modeling package for the Smartkeg
# ----------------------------------------------------------------------------

from socket_server import SmartkegSocketServer
from process import ChildProcess
import time

class Model(ChildProcess):
    PERIODS = 7

    def __init__(self, pipe):
        super(Model, self).__init__(pipe)

    def centered_moving_avg(self, simple_moving_avg):
        """
        @Author:        Harrison Hubbell
        @Created:       11/04/2014
        @Description:   Calculate centered moving average from a simple
                        moving average
        """
        i = 0
        moving_avg = []

        while i < len(simple_moving_avg) - 1:
            avg = float(sum(simple_moving_avg[i:i + 1])) / 2.0
            moving_avg.append(avg)
            i += 1

        return moving_avg

    def simple_moving_avg(self, data_set, periods=None):
        """
        @Author:        Harrison Hubbell
        @Created:       11/04/2014
        @Description:   Create simple moving average set based on input
                        data and the optional number of periods.  If no
                        periods is specified it defaults to the model
                        PERIOD.
        """
        i = 0
        moving_avg = []
        if periods is None: periods = self.PERIODS

        while i < len(data_set) - periods:
            period_avg = float(sum(data_set[i:periods])) / float(periods)
            moving_avg.append(period_avg)
            i += 1

        return moving_avg

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
        
        while True:
            data = self.proc_recv()
            sma = self.simple_moving_avg(data)
            cma = self.centered_moving_avg(sma)
            
            ### XXX Do something with data

            self.proc_send(self.model)
            

        """self.server.set_response(json.dumps(self.model))

        while True:
            beer_data = self.proc_poll_recv()
            if beer_data:
                self.calculate_model(beer_data)
                self.server.set_response(json.dumps(self.model))
            
            self.server.respond()
            time.sleep(0.1)"""
