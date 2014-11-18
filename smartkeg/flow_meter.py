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
    _PINTS_PER_LITER = 2.11338
    _PULSES_PER_LITER = 450.00
    _TIMEOUT = 2.00

    def __init__(self, pipe, gpio, pin):
        super(FlowMeter, self).__init__(pipe)
        self.GPIO = gpio
        self.pin = pin
        self.units = 'Pints'
        self.ticks = 0

    def convert_ticks_to_pints(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Converts flow meter ticks to pint value. According
                        to documentation, the flow meter used:
                            Liquid Flow Meter - Plastic 1/2" NPS Threaded
                        from Adafruit (Product ID 828) calculates 
                        1 Liter = 450 Pulses.
                        
        """
        self.pints = (float(self.ticks) / self._PULSES_PER_LITER) * self._PINTS_PER_LITER

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
        while True:
            if self.ticks > 0 and time.time() - self.last_tick > self._TIMEOUT:
                self.convert_ticks_to_pints()
                self.logger.log(('[Flow Meter]', 'flow detected', self.pints, self.units))                
                self.proc_send(self.pints)
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

