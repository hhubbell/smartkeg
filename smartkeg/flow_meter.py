# ----------------------------------------------------------------------------
# Filename:     flow_meter.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Reads flow from flow meter.
# TODO:         The main method need some serious refactoring, particularly:
#                   > NOT ALL ONE METHOD
#                   > Event Based
#                   > Return data to parent proc
#               Create FlowMeter class to handle checking flow, that the
#               FlowMeterReader object controls
# ----------------------------------------------------------------------------

from multiprocessing import Pipe
import RPi.GPIO as GPIO
import time

class FlowMeterReader:
    _TIME_ACCY = 1000
    _TIMEOUT = 1

    def __init__(self, pipe, gpio, data_pin):
        self.pipe = pipe
        self.GPIO = gpio
        self.data_pin = data_pin
        self.pouring = False
        self.pin_state = False

    def setup_data_pin(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   prepares the data pin for incoming voltage
        """
        self.GPIO.setup(self.data_pin, self.GPIO.IN)

    def main(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   The main loop. checks for a pour and handles 
                        it if true.
        """
        self.setup_data_pin()
        timeout = self._TIMEOUT * self._TIME_ACCY
        last_pin_state = self.pin_state
        now = int(time.time() * self._TIME_ACCY)
        pin_change = now
        last_pin_change = now

        while True:
            if self.GPIO.input(self.data_pin):
                self.pin_state = True
            else:
                self.pin_state = False

            if self.pin_state != last_pin_state and self.pin_state is True:
                if self.pouring is False:
                    pour_start = now
                    pin_change = now

                self.pouring = True
                
                pin_delta = pin_change - last_pin_change
                if pin_delta < timeout:
                    hertz = 1000.000 / pin_delta
                    flow = hertz / (60 * 7.5)
                    liters += flow * (pin_delta / 1000.000)

            if self.pouring is True and self.pin_state == last_pin_state and now - last_pin_change > 3000:
                self.pouring = False
                if liters_poured > 0.1:
                    self.pipe.send(liters_poured)
                    liters_poured = 0

            last_pin_change = pin_change
            last_pin_state = self.pin_state

                    
    

