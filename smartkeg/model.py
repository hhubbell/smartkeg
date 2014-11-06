# ----------------------------------------------------------------------------
# Filename:     model.py
# Author:       Harrison Hubbell
# Date:         10/07/2014
# Description:  Statistical modeling package for the Smartkeg. All "Models"
#               MUST have a forecast() methed.
# ----------------------------------------------------------------------------

from process import ChildProcess

class SmartkegModelMaker(ChildProcess):
    def __init__(self, pipe, model):
        super(SmartkegModelMaker, self).__init__(pipe)
        self.model = model

    def main(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/05/2014
        @Description:   Main method of SmartkegModelMaker. Is responsible for
                        receiving data and calculating the forecast model.
        """
        while True:
            data = self.proc_recv()
            forecast = self.model.forecast()
            self.log_message(['[ModelMaker]','New model:', self.model.to_string()])
            self.proc_send(forecast)


class TimeSeriesRegression(object):
    def __init__(self, periods):
        self.periods = periods

    def forecast(self, data):
        """
        @Author:        Harrison Hubbell
        @Created:       11/05/2014
        @Description:   Creates the time-series regression model.
        """
        self.trend = self.calculate_regression_line(data)
        self.seasonality = self.calculate_seasonal_indices(data)


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

        self.intercept = (sy * ssx - sx * sxy) / (n * ssx - sx ** 2)
        self.slope = (n * sxy - sx * sy) / (n * ssx - sx ** 2)

        return lambda x: self.intercept + self.slope * x

    def calculate_seasonal_indicies(self, data):
        """
        @Author:        Harrison Hubbell
        @Created:       11/04/2104
        @Description:   Calculate the seasonal indecies for each period.
        """
        i = 0
        seasonal_indicies = []
        
        if self.periods % 2 == 0:
            sma = self.simple_moving_avg(data)
            cma = self.centered_moving_avg(sma)
        else:
            # No need to center the MA here because periods is odd.
            cma = self.simple_moving_avg(data)

        while i < self.periods:
            seasonal_indicies.append(sum(cma[i::i + self.periods]))
            i += 1
            
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

    def simple_moving_avg(self, data_set):
        """
        @Author:        Harrison Hubbell
        @Created:       11/04/2014
        @Description:   Create simple moving average set based on input
                        data and the number of periods
        """
        i = 0
        moving_avg = []

        while i < len(data_set) - self.periods:
            period_avg = float(sum(data_set[i:self.periods])) / float(self.periods)
            moving_avg.append(period_avg)
            i += 1

        return moving_avg

    def to_string(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/05/2014
        @Description:   Returns a string representation of the time-series
                        regression model.
        """
        T = "(" + str(self.intercept) + " + " + str(self.slope) + "(x))"
        S = "(" + str(self.seasonal_index) + ")"

        return T + " * " + S
