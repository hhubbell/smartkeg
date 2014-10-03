# ----------------------------------------------------------------------------
# Filename:     main.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Is responsible for spooling and monitoring smartkeg processes, 
#               and handing data interaction between these parts.
# ----------------------------------------------------------------------------

from multiprocessing import Process, Pipe
from ConfigParser import ConfigParser
from database_interface import Database_Interface
from led_display import LED_Display
from smartkeg_server import Smartkeg_Server
from flow_meter import Flow_Meter
from temperature_sensor import Temperature_Sensor
import RPi.GPIO as GPIO
import time

class Smartkeg:
    _CONFIG_PATH = 'etc/config.cfg'

    # This should probably become a seperate module
    _QUERY = {
        'INSERT': {
            'POUR': """
                INSERT INTO Pour (keg_id, volume)
                VALUES (%s, %s)
            """,
            'FRIDGE_TEMP': """
                INSERT INTO FridgeTemp (fridge_id, sensor_id, temperature)
                VALUES (%s, %s, %s)
            """
        },
        'SELECT': {
            'KEG_ID': """
                SELECT id FROM Keg WHERE now_serving = 1
            """,
            'VOLUME_REMAINING': """
                SELECT *** FROM *** JOIN *** WHERE ***
            """,
            'PERCENT_REMAINING': """
                
            """
        }
    }
    
    def __init__(self):
        self.dbi = self.set_database_connection()
        self._temp_read_interval = 0
        self.percent_remaining = self.get_percent_remaining()
        self.current_keg = self.get_current_keg()
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

    def set_next_read(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Handles setting the next temperature
                        read time based on interval.
        """
        self.next_read = time.time() + self._temp_read_interval

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
        
    def get_volume_remaining(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Returns remaining volume of beer left in
                        the keg.
        """
        return self.dbi.SELECT(self.QUERY['SELECT']['VOLUME_REMAINING'])

    def get_percent_remaining(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Returns remaining volume of beer left in
                        the keg as a percentage of the keg's capacity.
        """
        return self.dbi.SELECT(self.QUERY['SELECT']['PERCENT_REMAINING'])            
    
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
   
    def proc_recv(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @created:       08/31/2014
        @Description:   Receives data from a process via its pipe.
        """
        return self.PIPE[proc_name]['FROM'].recv()
   
    def proc_send(self, proc_name, payload):
        """
        @Author:        Harrison Hubbell
        @created:       08/31/2014
        @Description:   Receives data to a process via its pipe.
        """
        self.PIPE[proc_name]['TO'].send(payload)

    def proc_start_all(self):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Starts all processes in the PROC dict.
        """
        for p in self.procs:
            self.procs[p].start()

    # --------------------
    # PROC EVENT HANDLERS
    # --------------------
    def handle_flow_meter(self):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Checks for new pour information and writes
                        to database when a pour occurs
        """
        pour = self.proc_recv(PROC['FLO'])
        if pour:
            self.dbi.INSERT(self.QUERY['INSERT']['POUR'], (self.current_keg, pour))

    def handle_led_display(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Checks for a new remaining volume and tells 
                        the LED process how many rows to light.
        """
        prev_rem = self.percent_remaining
        new_rem = self.get_percent_remaining()

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
        else:
            rows = None
        
        self.proc_send(PROC['LED'], rows)
            
    def handle_temperature_sensor(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Checks if it is time to read the temperature
                        sensors again and if true, gets current temp
                        data and logs to the database.
        """
        now = time.time()
        if now == self.next_read:
            self.proc_send(PROC['TMP'], 'read')
            temps = self.proc_recv(PROC['TMP'])
            self.dbi.INSERT(self.QUERY['INSERT']['TEMP'], temps)
            self.set_next_read()

    # --------------------
    # PROCS
    # --------------------
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

        flo = FlowMeterReader(conn, GPIO, pin)
        flo.main()

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

        self.set_next_read()

        tmp = TemperatureSensorReader(conn, sensors, thermo_dir, filename)
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
        smartkeg.handle_flow_meter()
        smartkeg.handle_led_display()
        smartkeg.handle_temperature_sensor()
