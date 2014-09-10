# ----------------------------------------------------------------------------
# Filename:     temperature_sensor.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Reads temperatures from sensors, and returns these values 
#               to its parent process.  This Class expects a DS18B20 3-pin
#               sensor to generate temperature values.
# ----------------------------------------------------------------------------

from multiprocessing import Pipe

class Temperature_Sensor:
    def __init__(self, pipe, sensors, therm_dir, filename):
        self.pipe = pipe
        self.sensors = sensors
        self.therm_directory = therm_dir
        self.filename = filename

    def read_temperature(self, sensor):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Opens the temperature file in the sensor directory
                        and reads its value. Temperatures are located in a 
                        file because the DS18B20 is a digital 3-pin sensor
                        and writes directly using STDIN.
        """
        sensor_path = self.therm_directory + sensor + '/' + self.filename
        with open(sensor_path, 'r') as thermo:
            temperature = re.split('t=', thermo.read())
            return float(temperature[1]) / 1000.00

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
            job = self.pipe.recv()
            if job == 'read':
                temperatures = []
                for s in self.sensors:
                    c_temp = self.read_temperature(s)
                    temperatures[] = ('NULL', s, celcius_to_fahrenheit(c_temp))
                self.pipe.send(temperatures)

