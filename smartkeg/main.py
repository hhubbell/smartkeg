# ----------------------------------------------------------------------------
# Filename:     main.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Is responsible for spooling and monitoring smartkeg processes, 
#               and handing data interaction between these parts.
# ----------------------------------------------------------------------------

from ConfigParser import ConfigParser
from process import ParentProcess
from database_interface import DatabaseInterface
from flow_meter import FlowMeterReader
from led_display import LEDDisplay
from temperature_sensor import TemperatureSensorReader
from model import Model
from query import Query
import RPi.GPIO as GPIO
import time

class Smartkeg(ParentProcess):
    _CONFIG_PATH = 'etc/config.cfg'
    
    def __init__(self):
        super(Smartkeg, self).__init__()
        self.dbi = self.set_database_connection()
        self.query_set_current_keg()
        #self.percent_remaining = self.get_percent_remaining()
        #self.current_keg = self.get_current_keg()

    # --------------------
    # SETTERS
    # --------------------
    def set_database_connection(self):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Creates a database interface for inserting and 
                        selecting data.
        """
        HEADER = 'MariaDB'
        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        usr = cfg.get(HEADER, 'usr')
        pwd = cfg.get(HEADER, 'pwd')
        dbn = cfg.get(HEADER, 'dbn')
        adr = cfg.get(HEADER, 'adr')
        return DatabaseInterface(adr, dbn, usr, pwd)

    # --------------------
    # GETTERS
    # --------------------
    def get_current_keg(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Descreption:   Returns current keg id
        """
        return self.dbi.SELECT(self.QUERY['SELECT']['KEG_ID'])

    # --------------------
    # QUERY SET METHODS
    # --------------------
    def query_set_current_keg(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Returns current keg id
        """
        self.current_kegs = self.dbi.SELECT(Query.SELECT_KEG_ID)

    # --------------------
    # QUERY GET METHODS
    # --------------------
    def query_get_percent_remaining(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Returns remaining volume of beer left in
                        the keg as a percentage of the keg's capacity.
        """
        return self.dbi.SELECT(Query.SELECT_PERCENT_REMAINING)
        
    def get_volume_remaining(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Returns remaining volume of beer left in
                        the keg.
        """
        return self.dbi.SELECT(Query.SELECT_VOLUME_REMAINING)

    # --------------------
    # PROC EVENT HANDLERS
    # --------------------
    def handle_flow_meter(self, proc_name, callback=None, args=None):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Checks for new pour information and writes
                        to database when a pour occurs
        """
        # XXX This will be set elsewhere, eventually when a keg is inserted into the 
        # db (either through the web or through the gui.
        self.current_keg = 1
        pour = self.proc_poll_recv(proc_name)
        if pour:
            self.dbi.INSERT(Query.INSERT_POUR, params=[(self.current_keg, pour)])

    def handle_led_display(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Checks for a new remaining volume and tells 
                        the LED process how many rows to light.
        """
        prev_rem = None #self.percent_remaining
        new_rem = None #self.get_percent_remaining()

        if new_rem != prev_rem:
            self.percent_remaining = new_rem
            if self.percent_remaining > .75:
                rows = 4
            elif self.percent_remaining > .5:
                rows = 3
            elif self.percent_remaining > .25:
                rows = 2
            else:
                rows = 1
                
            self.proc_send(proc_name, rows)

    def handle_model(self, proc_name):
        """
        @Author:        Harrison Hubbell

        
        """
        return
            
    def handle_temperature_sensor(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Checks if it is time to read the temperature sensors.
                        If true, gets current temp data and logs to the 
                        database.  This method blocks processing until
                        temperatures are returned, or an exception is thrown
                        by the TemperatureSensorReader.
        """
        #TODO: Give value to fridge_id
        fridge_id = 'NULL'
        
        temperatures = self.proc_poll_recv(proc_name)
        if temperatures:
            temp_tuples = []
            for sensor in temps:
                temp_tuples.append((fridge_id, sensor, temps[sensor]))

            self.dbi.INSERT(Query.INSERT_FRIDGE_TEMP, temps_tuples)

    # --------------------
    # PROCS
    # --------------------
    def spawn_flow_meter(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2104
        @Description:   Creates the Flow Meter process.
        """
        HEADER = 'SmartkegFlowMeter'

        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        pin = cfg.getint(HEADER, 'data_pin')

        flo = FlowMeterReader(conn, GPIO, pin)
        flo.main()

    def spawn_led_display(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2104
        @Description:   Creates the LED Display process.
        """
        led = LEDDisplay(conn, GPIO)
        led.main()

    def spawn_model(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2104
        @Description:   Creates the Modeling process.
        """        
        mod = Model(conn)
        mod.main()

    def spawn_temp_sensor(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2104
        @Description:   Creates the Temperature Sensor process.
        """
        HEADER = 'SmartkegTemperatureSensor'

        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        interval = cfg.getfloat(HEADER, 'interval')
        thermo_dir = cfg.get(HEADER, 'dir')
        filename = cfg.get(HEADER, 'file')
        sensors = cfg.get(HEADER, 'sensors').split(',')
        
        tmp = TemperatureSensorReader(conn, interval)
        for sensor in sensors:
            tmp.sensor_add(sensor, thermo_dir, filename)
            
        tmp.main()

if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)

    PROC = {
        'FLO': 'flow_meter',        
        'LED': 'led_display',
        'MOD': 'model',
        'TMP': 'temperature_sensor'
    }

    smartkeg = Smartkeg()
    smartkeg.proc_add(PROC['FLO'], target=smartkeg.spawn_flow_meter, pipe=True)    
    smartkeg.proc_add(PROC['LED'], target=smartkeg.spawn_led_display, pipe=True)
    smartkeg.proc_add(PROC['TMP'], target=smartkeg.spawn_temp_sensor, pipe=True)    
    smartkeg.proc_add(PROC['MOD'], target=smartkeg.spawn_model, pipe=True)
    smartkeg.proc_start_all()
 
    while True:
        smartkeg.handle_flow_meter(PROC['FLO'])
        smartkeg.handle_led_display(PROC['LED'])
        smartkeg.handle_temperature_sensor(PROC['TMP'])
        smartkeg.handle_model(PROC['MOD'])
        time.sleep(0.1)
