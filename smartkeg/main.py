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
from socket_server import SmartkegSocketServer
from model import SmartkegModelMaker, TimeSeriesRegression
from query import Query
import RPi.GPIO as GPIO
import time
import json

class Smartkeg(ParentProcess):
    _BASE_DIR = '/usr/local/src/smartkeg/'
    _CONFIG_PATH = _BASE_DIR + 'etc/config.cfg'
    TSR_PERIODS = 7

    def __init__(self):
        super(Smartkeg, self).__init__()
        self.dbi = self.set_database_connection()

        # This is an example of the JSON being sent.
        self.model = {
            'consumption': {
                'x': {
                    50: {
                        'y':[3, 5, 17, 23, 8, 6, 13, 14, 5, 16],
                        'mean': None,
                    },
                    150: {
                        'y':[6, 3, 7, 13, 16, 8, 16, 3, 4, 6],
                        'mean': None,
                    },
                    250: {
                        'y':[3, 8, 17, 9, 16, 8, 16, 13, 10, 6],
                        'mean': None,
                    },
                    350: {
                        'y':[9, 18, 56, 13, 6, 28, 16, 23, 24, 36],
                        'mean': None,
                    },
                    450: {
                        'y':[33, 43, 67, 53, 56, 48, 46, 33, 44, 36],
                        'mean': None,
                    },
                    550: {
                        'y':[93, 83, 77, 93, 96, 98, 116, 63, 64, 36],
                        'mean': None,
                    },
                    650: {
                        'y':[83, 83, 77, 93, 96, 98, 90, 43, 44, 46],
                        'mean': None,
                    }
                },
                'radius': 2,
                'style': 'circle'
            },
            'remaining': {
                'y': 94.13241234
            },
            'beer_info': {
                'brand': 'Fiddlehead',
                'name': 'Mastermind',
                'type': 'Ale',
                'subtype': 'Double IPA',
                'ABV': 8.2,
                'IBU': '???',
                'rating': 5
            }
        }


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

        self.logger.log('Initializing Database Connection.')

        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        usr = cfg.get(HEADER, 'usr')
        pwd = cfg.get(HEADER, 'pwd')
        dbn = cfg.get(HEADER, 'dbn')
        adr = cfg.get(HEADER, 'adr')
        return DatabaseInterface(adr, dbn, usr, pwd, logger=self.logger)

    # --------------------
    # GETTERS
    # --------------------
    # XXX Necessary?
    def get_current_keg(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Descreption:   Returns current keg id
        """
        return self.dbi.SELECT(Query.SELECT_KEG_ID)

    # --------------------
    # QUERY METHODS
    # --------------------
    def query_insert_fridge_temperature(self, temperature):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   INSERTS the fridge temperature values.
        """
        self.dbi.INSERT(Query.INSERT_FRIDGE_TEMP, params=temperature)

    def query_insert_pour(self, pour):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   INSERTS the pour value.
        """
        self.dbi.INSERT(Query.INSERT_POUR, params=[(self.current_keg, pour)])

    def query_select_current_keg(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   Returns current keg id
        """
        self.current_kegs = self.dbi.SELECT(Query.SELECT_KEG_ID)

    def query_select_percent_remaining(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Returns remaining volume of beer left in
                        the keg as a percentage of the keg's capacity.
        """
        return self.dbi.SELECT(Query.SELECT_PERCENT_REMAINING)

    def query_select_volume_remaining(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Returns remaining volume of beer left in
                        the keg.
        """
        return self.dbi.SELECT(Query.SELECT_VOLUME_REMAINING)

    # --------------------
    # FLOW METER
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

    def flow_meter_get_pour(self, proc):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   pulls the last pour from the pipe connected to the
                        flow meter process, and sets the last_pour field as
                        that value.  Returns true if a pour is detected,
                        false otherwise.
        """
        pour = self.proc_poll_recv(proc)
        res = None

        if pour:
            res = True
            self.last_pour = pour
        else:
            res = False

        return res

    # --------------------
    # LED DISPLAY
    # --------------------
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

    # --------------------
    # MODEL
    # --------------------
    def handle_model(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @Created:
        @Description:   For now, it is just example data.

        """
        self.proc_send(proc_name, 'EXAMPLE DATA')
        self.model = self.proc_recv(proc_name)

    # --------------------
    # SOCKET SERVER
    # --------------------
    def socket_server_set_response(self, proc_name, response):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   Updates the Socket Server procs response.
        """
        self.proc_send(proc_name, json.dumps(response))

    # --------------------
    # TEMPERATURE SENSOR
    # --------------------
    def temperature_sensor_read(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   Polls the temperature sensor proc and gets the
                        values if there has been a reading.  Returns true
                        if a reading has occured and false otherwise.
        """
        temperatures = self.proc_poll_recv(proc_name)
        res = None

        if temperatures:
            res = True
            temp_tuples = []
            for sensor in temps:
                temp_tuples.append((sensor, temps[sensor]))

        else:
            res = False

        return res

    # XXX Reconsider
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
        @Created:       08/31/2014
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
        @Created:       08/31/2014
        @Description:   Creates the LED Display process.
        """
        led = LEDDisplay(conn, GPIO)
        led.main()

    def spawn_model(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       10/07/2014
        @Description:   Creates the Modeling process.
        """
        mod = SmartkegModelMaker(TimeSeriesRegression(self.TSR_PERIODS))
        mod.main()

    def spawn_socket_server(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   Creates the Socket Server process
        """
        HEADER = 'SmartkegSocketServer'
        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        host = cfg.get(HEADER, 'host')
        port = cfg.getint(HEADER, 'port')

        soc = SmartkegSocketServer(conn, host, port)
        soc.set_response(soc.update_id, json.dumps(self.model))
        soc.main()


    def spawn_temp_sensor(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/20q4
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
        'SOC': 'socket_server',
        'TMP': 'temperature_sensor'
    }

    smartkeg = Smartkeg()
    smartkeg.proc_add(PROC['FLO'], target=smartkeg.spawn_flow_meter, pipe=True)
    smartkeg.proc_add(PROC['LED'], target=smartkeg.spawn_led_display, pipe=True)
    smartkeg.proc_add(PROC['MOD'], target=smartkeg.spawn_model, pipe=True)
    smartkeg.proc_add(PROC['SOC'], target=smartkeg.spawn_socket_server, pipe=True)
    smartkeg.proc_add(PROC['TMP'], target=smartkeg.spawn_temp_sensor, pipe=True)
    smartkeg.proc_start_all()

    smartkeg.socket_server_set_response(PROC['SOC'], smartkeg.model)

    while True:
        if smartkeg.flow_meter_get_pour(PROC['FLO']):
            smartkeg.query_insert_pour(smartkeg.last_pour)

            ### XXX Build new data structure ###

            smartkeg.handle_led_display(PROC['LED'])
            smartkeg.handle_model(PROC['MOD'])
            smartkeg.socket_server_set_response(PROC['SOC'], smartkeg.model)

        if smartkeg.temperature_sensor_read(PROC['TMP']):
            smartkeg.query_insert_fridge_temperature(smartkeg.fridge_temperature)

            ### XXX Build new data structure ###

            smartkeg.socket_server_set_response(PROC['SOC'], smartkeg.model)

        time.sleep(0.1)
