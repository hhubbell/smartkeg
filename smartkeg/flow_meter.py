# ----------------------------------------------------------------------------
# Filename:     flow_meter.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Reads flow from flow meter. For the current scope of the 
#               project ther is only one flow meter per kegerator.  The 
#               FlowMeterReader object can however, with some modification,
#               be made to handle multiple FlowMeters in form of child procs.
# ----------------------------------------------------------------------------

from process import ChildProcess
import RPi.GPIO as GPIO
import time

class FlowMeter(ChildProcess):
    _TIME_ACCY = 1000
    _TIMEOUT = 1
    
    def __init__(self, pipe, gpio, pin):
        super(FlowMeter, self).__init__(pipe)
        self.GPIO = gpio
        self.pin = pin
        self.ticks = 0

    def convert_ticks_to_pints(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Converts flow meter ticks to pint value.
        """
        # FIXME
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
        self.last_tick = time.time()
        
        while True:
            if time.time() - self.last_tick > self._TIMEOUT and self.ticks > 0:
                self.convert_ticks_to_pints()
                self.proc_send(self.last_pour)
                self.logger.log(['[Flow Meter]', self.last_pour])
                self.reset_ticks()

            if self.GPIO.event_detected(self.pin):
                self.ticks += 1
                self.last_tick = time.time()
            else:
                time.sleep(0.1)

class FlowMeterReader(ChildProcess):
    def __init__(self, pipe, gpio, pin):
        super(FlowMeterReader, self).__init__(pipe)
        self.flow_meter = FlowMeter(pipe, gpio, pin)
        
    def main(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Starts monitor the FlowMeter for pouring
        """
        self.flow_meter.setup_data_pin()
        self.flow_meter.monitor_flow()
        
