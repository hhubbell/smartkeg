#
# Filename:     flow_meter.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Reads flow from flow meter.
#

from multiprocessing import Process, Queue
from .query import Query
import RPi.GPIO as GPIO
import logging
import time

class FlowMeter(object):
    _PINTS_PER_LITER = 2.11338
    _PULSES_PER_LITER = 450.00
    _TIMEOUT = 2.00

    def __init__(self, pin, conn):
        self.pin = pin
        self.conn = conn
        self.units = 'Pints'
        self.ticks = 0
        self.setup_data_pin()

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
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.RISING)

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
                self.conn.put(self.pints)
                self.reset_ticks()

            if GPIO.event_detected(self.pin):
                self.ticks += 1
                self.last_tick = time.time()
            else:
                time.sleep(0.1)

class FlowMeterController(object):
    def __init__(self, pins, pipe=None, dbi=None):
        self.dbi = dbi        
        self.fmq = Queue()
        self.fms = self.register_meters(pins)        
        self.pipe = pipe

    def register_meters(self, pins):
        """
        @Author:        Harrison Hubbell
        @Created:       03/05/2015
        @Description:   Create a FlowMeter thread for each pin which allows
                        the controller to accept flow input from multiple 
                        taps.
        """
        fms = []
        for pin in pins:
            fm = FlowMeter(pin, self.fmq)
            p = Process(target=fm.monitor_flow())
            p.start()
            
            fms.append(fm)

        return fms

    def run(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Starts monitor the FlowMeter for pouring
        """
        while True:
            while not fmq.empty():
                data = fmq.get()
                logging.info('Flow detected {}'.format(data))
                self.pipe.send(data)

