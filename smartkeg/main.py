# ----------------------------------------------------------------------------
# Filename:     main.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Is responsible for spooling and monitoring smartkeg processes, 
#               and handing data interaction between these parts.
# ----------------------------------------------------------------------------

from multiprocessing import Process, Pipe
from ConfigParser import ConfigParser
from database_interface import DatabaseInterface
from led_display import LEDDisplay
from smartkeg_server import SmartkegServer
from flow_meter import FlowMeterReader
from temperature_sensor import TemperatureSensorReader
from query import Query
import RPi.GPIO as GPIO
import time

class Smartkeg:
    _CONFIG_PATH = 'etc/config.cfg'
    
    def __init__(self):
        self.dbi = self.set_database_connection()
        self.query_set_current_keg()

        #self.percent_remaining = self.get_percent_remaining()
        #self.current_keg = self.get_current_keg()
        self.procs = {}
        self.PIPE = {}

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

    def set_next_read_time(self, interval):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Handles setting the next temperature
                        read time based on interval.
        """
        self.next_read = time.time() + interval

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
    # PROC METHODS
    # --------------------
    def proc_add(self, proc_name, target=None, pipe=None):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Adds a process and manages creating the pipes 
                        between both nodes.
        """
        args = None

        if pipe:
            self.PIPE[proc_name] = {'TO': None, 'FROM': None}
            self.PIPE[proc_name]['TO'], self.PIPE[proc_name]['FROM'] = Pipe()
            args = (self.PIPE[proc_name]['FROM'],)

        self.procs[proc_name] = Process(name=proc_name, target=target, args=args)
   
    # XXX Re-evaluate need for this method.
    def proc_recv(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @created:       08/31/2014
        @Description:   Receives data from a process via its pipe.
        """
        node = self.PIPE[proc_name]['FROM']
        if node.poll():
            return node.recv()
   
    def proc_send(self, proc_name, payload):
        """
        @Author:        Harrison Hubbell
        @created:       08/31/2014
        @Description:   Sends data to an arbitrary process via its pipe.
        """
        self.PIPE[proc_name]['TO'].send(payload)

    def proc_start_all(self):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Starts all processes in the procs dict.
        """
        for p in self.procs:
            self.procs[p].start()

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
        if self.PIPE[proc_name]['TO'].poll():
            pour = self.PIPE[proc_name]['TO'].recv()
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
        
        now = time.time()
        if now == self.next_read:
            self.proc_send(proc_name, 'read')
            temps = self.PIPE[proc_name]['TO'].recv()
            
            temp_tuples = []
            for sensor in temps:
                temp_tuples.append((fridge_id, sensor, temps[sensor]))

            self.dbi.INSERT(Query.INSERT_FRIDGE_TEMP, temps)
            self.set_next_read_time(self._temp_read_interval)

    # --------------------
    # PROCS
    # --------------------
    def spawn_flow_meter(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2104
        @Description:   Creates the Flow Meter process
        """
        HEADER = 'SmartkegFlowMeter'

        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        pin = cfg.getint(HEADER, 'data_pin')

        flo = FlowMeterReader(GPIO, pin, conn)
        flo.main()

    def spawn_led_display(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2104
        @Description:   Creates the LED Display process
        """
        led = LEDDisplay(conn, GPIO)
        led.main()

    def spawn_server(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2104
        @Description:   Creates the Server Process process
        """
        HEADER = 'SmartkegServer'
        
        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        host = cfg.get(HEADER, 'host')
        port = cfg.getint(HEADER, 'port')
        
        srv = SmartkegServer(conn, host, port)
        srv.main()

    def spawn_temp_sensor(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2104
        @Description:   Creates the Temperature Sensor process
        """
        HEADER = 'SmartkegTemperatureSensor'

        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        self._temp_read_interval = cfg.getfloat(HEADER, 'interval')
        thermo_dir = cfg.get(HEADER, 'dir')
        filename = cfg.get(HEADER, 'file')
        sensors = cfg.get(HEADER, 'sensors').split(',')

        self.set_next_read_time(self._temp_read_interval)

        tmp = TemperatureSensorReader(conn)
        for sensor in sensors:
            tmp.sensor_add(sensor, thermo_dir, filename)
            
        tmp.main()

if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)

    PROC = {
        'LED': 'led_display',
        'SRV': 'server',
        'FLO': 'flow_meter',
        'TMP': 'temperature_sensor'
    }

    smartkeg = Smartkeg()
    smartkeg.proc_add(PROC['LED'], target=smartkeg.spawn_led_display, pipe=True)
    smartkeg.proc_add(PROC['SRV'], target=smartkeg.spawn_server, pipe=True)
    smartkeg.proc_add(PROC['FLO'], target=smartkeg.spawn_flow_meter, pipe=True)
    smartkeg.proc_add(PROC['TMP'], target=smartkeg.spawn_temp_sensor, pipe=True)
    smartkeg.proc_start_all()
 
    while True:
        smartkeg.handle_flow_meter(PROC['FLO'])
        smartkeg.handle_led_display(PROC['LED'])
        smartkeg.handle_temperature_sensor(PROC['TMP'])
        time.sleep(0.1)
