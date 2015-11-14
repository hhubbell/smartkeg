#
# Filename:     led_display.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Manages lighting the LED display on the kegerator based on
#               the amount of beer left in the keg.  The LEDs are
#               multiplexed to limit the amount of gpio pins required to
#               light each row, as well as saving some energy over lighting
#               all rows at once; approximately 120 mA.  Multiplexing is
#               expensive however, and the perfomance of the loop - starting
#               the time a row lights and stopping when the row is lit
#               again - must not fall below 50Hz - to prevent noticable
#               light flicker.
#

import time

class LEDDisplay(object):
    ROW = [
        [15, 13, 11],
        [13, 15, 11],
        [15, 11, 13],
        [11, 15, 13]
    ]

    def __init__(self, pipe, gpio):
        self.gpio = gpio
        self.pipe = pipe
        self.rows = 0

    def light(self, row):
        """
        @author:        Harrison Hubbell
        @created:       08/31/2014
        @description:   Lights a given row of LEDs based on the List of
                        pin numbers passed in
        """
        self.gpio.setup(row[0], self.gpio.OUT)
        self.gpio.setup(row[1], self.gpio.OUT)
        self.gpio.setup(row[2], self.gpio.IN)

        self.gpio.output(row[0], self.gpio.HIGH)
        self.gpio.output(row[1], self.gpio.LOW)

    def get(self):
        """
        @author:        Harrison Hubbell
        @created:       10/05/2014
        @description:   Receives the number of rows to light and updates
                        if there is a new value.
        """
        if self.pipe.poll():
            self.rows = self.pipe.recv()

    def run(self):
        """
        @author:        Harrison Hubbell
        @created:       08/31/2014
        @description:   Lights each the number of rows it is told to light,
                        which is received from its parent proc.
        """
        while True:
            self.get()

            i = self.rows - 1
            while i >= 0:
                self.light(self.ROW[i])
                i -= 1

            # This prevents the CPU from running out of control.  If this
            # causes a noticable flicker in the display, it will have to
            # be refactored.
            time.sleep(0.1)
