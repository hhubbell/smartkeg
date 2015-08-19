#
# Filename:     temperature_sensor.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Reads temperatures from sensors, and returns these values
#               to its parent process.  This Class expects a DS18B20 3-pin
#               sensor to generate temperature values.
#

import logging
import time
import re

class TemperatureSensor(object):
    FILE = 'w1_slave'    
    SCALE = 1000.00

    def __init__(self, name, path):
        self.id = name
        self.sensor = '{}{}/{}'.format(path, name, self.FILE)

    def read(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Opens the temperature file in the sensor path and
                        reads its value. Temperatures are located in a
                        file because the DS18B20 is a digital 3-pin sensor
                        and writes directly using STDIN.
        """
        temperature = None

        try:
            with open(self.sensor, 'r') as thermo:
                temperature = re.split('t=', thermo.read())
                temperature = float(temperature[1]) / self.SCALE
        except IOError as e:
            logging.error(e)

        return temperature


class TemperatureSensorManager(object):
    PATH = '/sys/bus/w1/devices/'

    def __init__(self, interval, sensors=None, path=None, filename=None, pipe=None, dbi=None):
        sensors = sensors if sensors is not None else []
        
        logging.info('Starting TemperatureSensorManager...')
        logging.info('Initializing with sensors {}'.format(sensors))

        self.interval = interval        
        self.path = path if path is not None else self.PATH
        self.pipe = pipe
        self.dbi = dbi
                
        self.sensors = [TemperatureSensor(x, self.path) for x in sensors]

    def add(self, *ids):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Creates dict of TemperatureSensor Objects.
        """
        self.sensors += [TemperatureSensor(x, self.path) for x in ids]

    def read(self, id):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Reads from the specified sensor.
        """
        sensor = next(x for x in self.sensors if x.id == id)

        if sensor:
            return sensor.read()
        else:
            raise IndexError

    def read_all(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Reads all sensors and returns a dict with the
                        associated temperature for each sensor.
        """
        return {x.id: x.read() for x in self.sensors}

    def convert(self, celcius):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Converts Celcius values to Fahrenheit.
        """
        return celcius * 1.8 + 32

    def run(self):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   When a read job is received get the current temperature
                        and return the data to the parent proc as a dict.
        """
        while True:
            fahr = {k: self.convert(v) for k, v in self.read_all().items() if v is not None}
            [logging.info('{} {} F'.format(k, v)) for k, v in fahr.items()]

            self.pipe.send(fahr)
            
            # TODO Log to database

            time.sleep(self.interval)
