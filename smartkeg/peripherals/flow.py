#
# Filename:     flow_meter.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Reads flow from flow meter.
#

from multiprocessing import Process, Queue
import RPi.GPIO as GPIO
import logging
import time

class FlowMeter(object):
    _PINTS_PER_LITER = 2.11338
    _PULSES_PER_LITER = 450.00
    TIMEOUT = 2.00

    def __init__(self, pin, conn):
        self.pin = pin
        self.conn = conn
        self.units = 'pints'
        self.ticks = 0
        self.last_tick = 0
        self.setup_data_pin()

        logging.info(
            'FlowMeter initialized on pin %s (units: %s)',
            self.pin, self.units
        )

    def to_pints(self, ticks):
        """
        @author:        Harrison Hubbell
        @created:       10/05/2014
        @description:   Converts flow meter ticks to pint value. According
                        to documentation, the flow meter used:
                            Liquid Flow Meter - Plastic 1/2" NPS Threaded
                        from Adafruit (Product ID 828) calculates
                        1 Liter = 450 Pulses.

        """
        return (ticks / self._PULSES_PER_LITER) * self._PINTS_PER_LITER

    def reset(self):
        """
        @author:        Harrison Hubbell
        @created:       10/05/2014
        @description:   Resets ticks to zero
        """
        self.ticks = 0

    def setup_data_pin(self):
        """
        @author:        Harrison Hubbell
        @created:       10/04/2014
        @description:   Prepares the data pin for incoming voltage
        """
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.RISING)

    def monitor(self):
        """
        @author:        Harrison Hubbell
        @created:       09/01/2014
        @description:   The main loop. checks for a pour and handles
                        it if true.
        """
        while True:
            if self.ticks > 0 and time.time() - self.last_tick > self.TIMEOUT:
                self.conn.put({
                    'pin': self.pin,
                    'amount': self.to_pints(self.ticks)
                })
                self.reset()

            if GPIO.event_detected(self.pin):
                self.ticks += 1
                self.last_tick = time.time()
            else:
                time.sleep(0.1)

class FlowMeterManager(object):
    def __init__(self, pins=None, pipe=None, dbi=None):
        pins = pins if pins is not None else []

        logging.info('Starting FlowMeterManager...')
        logging.info('Initializing with meters on pins %s', pins)

        self.fmq = Queue()
        self.meters = [Process(target=FlowMeter(x, self.fmq).monitor) for x in pins]
        self.pipe = pipe
        self.dbi = dbi

    def add(self, *pins):
        """
        @author:        Harrison Hubbell
        @created:       03/05/2015
        @description:   Create a FlowMeter thread for each pin which allows
                        the controller to accept flow input from multiple
                        taps.
        """
        self.meters += [Process(target=FlowMeter(x, self.fmq).monitor) for x in pins]

    def start(self, pin):
        meter = next(x for x in self.meters if x.id == id)

        if meter:
            return meter.start()
        else:
            raise IndexError

    def start_all(self):
        [x.start() for x in self.meters]

    def run(self):
        """
        @author:        Harrison Hubbell
        @created:       10/04/2014
        @description:   Starts monitor the FlowMeter for pouring
        """
        self.start_all()

        while True:
            while not self.fmq.empty():
                data = self.fmq.get()
                self.pipe.send(data)
                logging.info('Flow detected %s', data)


            time.sleep(0.1)

