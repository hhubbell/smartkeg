# ----------------------------------------------------------------------------
# Filename:     flow_meter.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Reads flow from flow meter.  For the current scope of the 
#               project ther is only one flow meter per kegerator.
# TODO:         The main method need some serious refactoring, particularly:
#                   > Event Based
#                   > Return data to parent proc
#               Create FlowMeter class to handle checking flow, that the
#               FlowMeterReader object controls.  
# ----------------------------------------------------------------------------

from multiprocessing import Pipe
import RPi.GPIO as GPIO
import time

class FlowMeter:
    _TIME_ACCY = 1000
    _TIMEOUT = 1
    
    def __init__(self, gpio, pin, pipe):
        self.pipe = pipe
        self.GPIO = gpio
        self.pin = pin
        self.ticks = 0

    def convert_ticks_to_pints(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Converts flow meter ticks to pint value.
        """
        self.last_pour = self.ticks

    def reset_ticks(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Resets ticks to zero
        """
        self.ticks = 0

    def setup_data_pin(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Prepares the data pin for incoming voltage
        """
        self.GPIO.setup(self.pin, self.GPIO.IN)
        self.GPIO.add_event_detect(self.pin, self.GPIO.RISING)

    def monitor_flow(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   The main loop. checks for a pour and handles 
                        it if true.
        """
        # TODO There still might be a better way to do this.
        self.last_tick = time.time()
        
        while True:
            if time.time() - self.last_tick > self._TIMEOUT and self.ticks > 0:
                self.convert_ticks_to_pints()
                self.pipe.send(self.last_pour)
                self.reset_ticks()

            if self.GPIO.event_detected(self.pin):
                self.ticks += 1
                self.last_tick = time.time()
            else:
                time.sleep(0.1)

class FlowMeterReader:
    def __init__(self, gpio, pin, pipe):
        self.pipe = pipe
        self.flow_meter = FlowMeter(gpio, pin, pipe)
        
    def main(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Starts monitor the FlowMeter for pouring
        """
        self.flow_meter.setup_data_pin()
        self.flow_meter.monitor_flow()
        
