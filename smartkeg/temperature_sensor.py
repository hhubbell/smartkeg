#
# Filename:     temperature_sensor.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Reads temperatures from sensors, and returns these values
#               to its parent process.  This Class expects a DS18B20 3-pin
#               sensor to generate temperature values.
#

from . import query
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
        @author:        Harrison Hubbell
        @created:       10/04/2014
        @description:   Opens the temperature file in the sensor path and
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
        @author:        Harrison Hubbell
        @created:       10/04/2014
        @description:   Creates dict of TemperatureSensor Objects.
        """
        self.sensors += [TemperatureSensor(x, self.path) for x in ids]

    def avg(self, vals):
        return sum(vals) / len(vals) if vals else 0

    def read(self, id):
        """
        @author:        Harrison Hubbell
        @created:       10/04/2014
        @description:   Reads from the specified sensor.
        """
        sensor = next(x for x in self.sensors if x.id == id)

        if sensor:
            return sensor.read()
        else:
            raise IndexError

    def read_all(self):
        """
        @author:        Harrison Hubbell
        @created:       10/04/2014
        @description:   Reads all sensors and returns a dict with the
                        associated temperature for each sensor.
        """
        return {x.id: x.read() for x in self.sensors}

    def convert(self, celcius):
        """
        @author:        Harrison Hubbell
        @created:       08/31/2014
        @description:   Converts Celcius values to Fahrenheit.
        """
        return celcius * 1.8 + 32

    def run(self):
        """
        @author:        Harrison Hubbell
        @created:       08/31/2014
        @description:   When a read job is received get the current temperature
                        and return the data to the parent proc as a dict.
        """
        while True:
            fahr = {k: self.convert(v) for k, v in self.read_all().items() if v is not None}
            
            if fahr:
                avg = self.avg([x for x in fahr.values()])

                [logging.info('{} {} F'.format(x[0], x[1])) for k, v in fahr.items()]
                logging.info('Average: {} F'.format(avg))
                
                with self.dbi as dbi:
                    dbi.insert(*query.set_temperature({'temperature': avg}))
                
                self.pipe.send(avg)

            time.sleep(self.interval)
