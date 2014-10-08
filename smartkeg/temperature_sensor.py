# ----------------------------------------------------------------------------
# Filename:     temperature_sensor.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Reads temperatures from sensors, and returns these values 
#               to its parent process.  This Class expects a DS18B20 3-pin
#               sensor to generate temperature values.
# ----------------------------------------------------------------------------

from process import ChildProcess
import time
import re

class TemperatureSensor:
    TEMP_SCALE = 1000.00
    
    def __init__(self, sensor_path, name):
        self.name = name
        self.sensor = sensor_path

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
        with open(self.sensor, 'r') as thermo:
            temperature = re.split('t=', thermo.read())
            self.temperature = float(temperature[1]) / self.TEMP_SCALE
        

class TemperatureSensorReader(ChildProcess):
    def __init__(self, pipe, interval):
        super(TemperatureSensorReader, self).__init__(pipe)
        self.interval = interval
        self.sensors = {}    

    def sensor_add(self, sensor, therm_dir, filename):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Creates dict of TemperatureSensor Objects.
        """
        path = therm_dir + sensor + '/' + filename
        self.sensors[sensor] = TemperatureSensor(path, sensor)

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
            temperatures[sensor] = self.sensors[sensor].get_temperature()

        return temperatures

    def celcius_to_fahrenheit(self, celcius):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Converts Celcius values to Fahrenheit.
        """
        return celcius * 1.8 + 32

    def main(self):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   When a read job is received get the current temperature
                        and return the data to the parent proc as a tuple.
        """
        while True:
            fahrenheit_temps = {}
            celcius_temps = self.sensor_read_all()
            for sensor in celcius_temps:
                fahrenheit_temps[sensor] = celcius_to_fahrenheit(celcius_temps[sensor])
                    
            self.proc_send(farenheit_temps)
            time.sleep(self.interval)

