# ----------------------------------------------------------------------------
# Filename:     led_display.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Manages lighting the LED display on the kegerator based on 
#               the amount of beer left in the keg.  The LEDs are multiplexed
#               to limit the amount of GPIO pins required to light each row, 
#               as well as saving some energy over lighting all rows at once;
#               approximately 120 mA.  Multiplexing is expensive however, and 
#               the perfomance of the loop - starting the time a row lights 
#               and stopping when the row is lit again - must not fall below 
#               50Hz - to prevent noticable light flicker.
# ----------------------------------------------------------------------------

from multiprocessing import Pipe

class LED_Display:
    ROW = [
        [15, 13, 11],
        [13, 15, 11],
        [15, 11, 13],
        [11, 15, 13]
    ]

    def __init__(self, pipe, gpio):
        self.pipe = pipe
        self.GPIO = gpio

    def light_row(self, row):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Lights a given row of LEDs based on the List of 
                        pin numbers passed in
        """
        self.GPIO.setup(row[0], self.GPIO.OUT)
        self.GPIO.setup(row[1], self.GPIO.OUT)
        self.GPIO.setup(row[2], self.GPIO.IN)

        self.GPIO.output(row[0], self.GPIO.HIGH)
        self.GPIO.output(row[1], self.GPIO.LOW)

    def main(self):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Lights each the number of rows it is told to light, 
                        which is received from its parent proc.
        """
        rows = self.pipe.recv()
        if rows:
            light = rows - 1
        else:
            light = 0

        while True:
            rows = self.pipe.recv()
            if rows and rows != light:
                light = rows
            i = light
            while i > 0:
                light_row(ROW[i])
