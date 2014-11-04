# ----------------------------------------------------------------------------
# Filename:     model.py
# Author:       Harrison Hubbell
# Date:         10/07/2014
# Description:  Statistical modeling package for the Smartkeg
# ----------------------------------------------------------------------------

from process import ChildProcess

class Model(ChildProcess):
    PERIODS = 7

    def __init__(self, pipe):
        super(Model, self).__init__(pipe)

    def calculate_regression_line(self, data):
        """
        @Author:        Harrison Hubbell
        @Created:       11/04/2014
        @Description:   Calculate the regression line based on given data.
                        Returns a lambda function of the trend line function.
        """
        y_vals = []
        x_vals = []
        x_y = []
        x_sq = []
        y_sq = []

        for i, x in enumerate(data):
            y = i + 1            
            y_vals.append(y)
            x_vals.append(x)
            x_y.append(x * y)
            x_sq.append(x ** 2)
            y_sq.append(y ** 2)

        n = len(data)
        sx = sum(x_vals)
        sy = sum(y_vals)
        sxy = sum(x_y)
        ssx = sum(x_sq)
        ssy = sum(y_sq)


        intercept = (sy * ssx - sx * sxy) / (n * ssx - sx ** 2)
        slope = (n * sxy - sx * sy) / (n * ssx - sx ** 2)

        self.log_message(['[Model]','New trend line:','y =', intercept, '+', slope, '(x)'])

        return lambda x: intercept + slope * x

    def calculate_seasonal_indicies(self, data, periods=None):
        """
        @Author:        Harrison Hubbell
        @Created:       11/04/2104
        @Description:   Calculate the seasonal indecies for each period.  If
                        no amount of periods is specified, it will default to
                        self.PERIODS.
        """
        sma = self.simple_moving_avg(data, periods=periods)
        cma = self.centered_moving_avg(sma)

        ### Find seasonal Indicies

        return seasonal_indicies

    def centered_moving_avg(self, simple_moving_avg):
        """
        @Author:        Harrison Hubbell
        @Created:       11/04/2014
        @Description:   Calculate centered moving average from a simple
                        moving average.
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
                        PERIODS.
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

            self.trend = self.calculate_regression_line(data)
            self.seasonality = self.calculate_seasonal_indices(data)

            self.proc_send(self.model)
