# ----------------------------------------------------------------------------
# Filename:     temperature_sensor.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Reads temperatures from sensors, and returns these values
#               to its parent process.  This Class expects a DS18B20 3-pin
#               sensor to generate temperature values.
# ----------------------------------------------------------------------------

import time
import re

class TemperatureSensor(object):
    TEMP_SCALE = 1000.00

    def __init__(self, sensor_path, name, logger):
        self.name = name
        self.sensor = sensor_path
        self.logger = logger

    def get_name(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Returns the sensor name.
        """
        return self.name

    def get_temperature(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Returns the temperature read.
        """
        return self.temperature

    def read(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Opens the temperature file in the sensor path and
                        reads its value. Temperatures are located in a
                        file because the DS18B20 is a digital 3-pin sensor
                        and writes directly using STDIN.
        """
        try:
            with open(self.sensor, 'r') as thermo:
                temperature = re.split('t=', thermo.read())
                self.temperature = float(temperature[1]) / self.TEMP_SCALE
        except IOError as e:
            self.logger.log(('[Temperature Sensor]', e))
            self.temperature = None



class TemperatureSensorReader(object):
    def __init__(self,  sensors, path, fname, interval, pipe=None, dbi=None, logger=None):
        self.dbi = dbi
        self.interval = interval
        self.logger = logger
        self.pipe = pipe
        self.sensors = {}

        for sensor in sensors:
            self.sensor_add(sensor, path, fname)

    def sensor_add(self, sensor, therm_dir, filename):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Creates dict of TemperatureSensor Objects.
        """
        path = therm_dir + sensor + '/' + filename
        self.sensors[sensor] = TemperatureSensor(path, sensor, self.logger)

    def sensor_read(self, name):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Reads from the specified sensor.
        """
        return self.sensor[name].read()

    def sensor_read_all(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Reads all sensors in the sensor dict, and
                        returns a dict with the associated sensor
                        for each temperature.
        """
        temperatures = {}
        for sensor in self.sensors:
            self.sensors[sensor].read()
            celcius_temp = self.sensors[sensor].get_temperature()

            if celcius_temp:
                temperatures[sensor] = celcius_temp

        return temperatures

    def celcius_to_fahrenheit(self, celcius):
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
        fahrenheit_temps = {}

        while True:
            celcius_temps = self.sensor_read_all()

            for sensor in celcius_temps:
                fahrenheit_temps[sensor] = self.celcius_to_fahrenheit(celcius_temps[sensor])
                self.logger.log(('[Temperature Sensor]', sensor, fahrenheit_temps[sensor], 'F'))

            if fahrenheit_temps: 
                self.pipe.send(fahrenheit_temps)

            time.sleep(self.interval)
