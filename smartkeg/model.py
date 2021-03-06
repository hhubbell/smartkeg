#
# Filename:     model.py
# Author:       Harrison Hubbell
# Date:         10/07/2014
# Description:  Statistical modeling package for the Smartkeg. All "Models"
#               MUST have a forecast() methed.
#

from __future__ import division, print_function
import logging
import math

class TimeSeriesRegression(object):
    def __init__(self, periods):
        self.periods = periods
        self.seasonal_indicies = []
        self.intercept = None
        self.prediction = None
        self.seasonality = None
        self.slope = None
        self.trend = None

    def __str__(self):
        """
        @author:        Harrison Hubbell
        @created:       11/05/2014
        @description:   Returns a string representation of the time-series
                        regression model.
        """
        t = '({} + {}(x))'.format(str(self.intercept), str(self.slope))
        s = '({})'.format(' + '.join(
            ['{}(s{})'.format(self.seasonality(x), x) for x in range(0, self.periods)]
        ))

        return t + ' * ' + s

    def forecast(self, data):
        """
        @author:        Harrison Hubbell
        @created:       11/05/2014
        @description:   Creates the time-series regression model.
        """
        self.trend = self.calculate_regression_line(data)
        self.seasonality = self.calculate_seasonal_indices(data)

        self.prediction = []

        start = len(data)
        end = start + self.periods

        for i in range(start, end):
            self.prediction.append(self.trend(i) + self.seasonality(i))

        return self.prediction

    def calculate_regression_line(self, data):
        """
        @author:        Harrison Hubbell
        @created:       11/04/2014
        @description:   Calculate the regression line based on given data.
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

    def calculate_seasonal_indices(self, data):
        """
        @author:        Harrison Hubbell
        @created:       11/04/2104
        @description:   Calculate the seasonal indecies for each period.
                        If periods is EVEN: The simple moving average must
                        be centered.
                        If periods is ODD:  The simple moving average is
                        already centered and no further calculation is
                        necessary.
        """
        self.seasonal_indicies = []
        season_avg = []
        i = 0

        if self.periods % 2 == 0:
            sma = self.simple_moving_avg(data)
            cma = self.centered_moving_avg(sma)
        else:
            cma = self.simple_moving_avg(data)

        rma = self.ratio_to_moving_avg(data, cma)

        while i < self.periods and i < len(rma):
            points = rma[i::self.periods]

            print(rma)
            print(self.periods)
            print(points)

            season_avg.append(sum(points) / len(points))
            i += 1

        for avg in season_avg:
            self.seasonal_indicies.append((avg - self.periods) / sum(season_avg))

        return lambda x: self.seasonal_indicies[(x % self.periods)] if len(self.seasonal_indicies) > x % self.periods else 0

    def centered_moving_avg(self, simple_moving_avg):
        """
        @author:        Harrison Hubbell
        @created:       11/04/2014
        @description:   Calculate centered moving average from a simple
                        moving average.
        """
        i = 0
        moving_avg = []

        while i < len(simple_moving_avg) - 1:
            avg = float(sum(simple_moving_avg[i:i + 1])) / 2.0
            moving_avg.append(avg)
            i += 1

        return moving_avg

    def ratio_to_moving_avg(self, data_set, cma):
        """
        @author:        Harrison Hubbell
        @created:       11/06/2014
        @description:   Calculate the ratio to moving average for the
                        centered moving average.  A little black magic
                        happens here because using 0 based indicies and
                        the number of periods allows the index of the
                        related observed value (to the CMA value) to be
                        found by taking the floor of self.periods / 2.
        """
        i = int(math.floor(self.periods / 2))
        ratio_to_ma = []

        for avg in cma:
            ratio_to_ma.append(data_set[i] / avg)
            i += 1

        return ratio_to_ma

    def simple_moving_avg(self, data_set):
        """
        @author:        Harrison Hubbell
        @created:       11/04/2014
        @description:   Create simple moving average set based on input
                        data and the number of periods
        """
        i = 0
        moving_avg = []

        while i <= len(data_set) - self.periods:
            period_avg = sum(data_set[i:self.periods]) / self.periods
            moving_avg.append(period_avg)
            i += 1

        return moving_avg
