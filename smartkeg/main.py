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
from http_server import SmartkegHTTPServer
from led_display import LEDDisplay
from temperature_sensor import TemperatureSensorReader
from socket_server import SmartkegSocketServer
from model import SmartkegModelMaker, TimeSeriesRegression
from query import Query
import RPi.GPIO as GPIO
import time
import json
import os

class Smartkeg(ParentProcess):
    _BASE_DIR = os.path.dirname(os.path.realpath(__file__)) + '/'
    _CONFIG_PATH = _BASE_DIR + 'etc/config.cfg'
    TSR_PERIODS = 7
    DOT_RADIUS = 3
    DOT_STYLE = 'circle'

    def __init__(self):
        super(Smartkeg, self).__init__()
        self.datagram = {}
        self.current_temp = None
        self.set_database_connection()
        self.set_fridge()
        self.set_kegs()

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

        self.dbi = DatabaseInterface(adr, dbn, usr, pwd, logger=self.logger)

    def set_datagram(self, key, value):
        """
        @Author:        Harrison Hubbell
        @Created:       11/20/2014
        @Description:   Sets the 'datagram' - the server response object.
        """
        self.datagram[key] = value

    def set_fridge(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/07/2014
        @Description:   Reads config file to get fridge name and queries
                        the database to set the fridge_id.
        """
        HEADER = 'Fridge'

        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        name = cfg.get(HEADER, 'name')

        self.fridge = self.query_select_fridge(name)[0]['id']

    def set_kegs(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/17/2014
        @Description:   Sets the current kegs.
        """
        self.kegs = []
        res = self.query_select_current_kegs()

        self.logger.log(res)

        for keg in res:
            self.kegs.append({
                'id': keg['keg_id'],
                'consumption': {
                    'days': [],
                    'radius': self.DOT_RADIUS,
                    'style': self.DOT_STYLE
                },
                'remaining': {
                    'value': keg['remaining']
                },
                'beer': {
                    'brand': keg['brewer'],
                    'name': keg['name'],
                    'type': keg['type'],
                    'subtype': keg['subtype'],
                    'abv': keg['abv'],
                    'ibu': keg['ibu'],
                    'rating': keg['rating']
                }
            })


    # --------------------
    # QUERY METHODS
    # --------------------
    def query_insert_temperatures(self, temperature_dict):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   Converts the dict to a list of tuples and
                        INSERTS the temperature values.
        XXX: For python3, items must be cast to a list().
        """
        items = temperature_dict.items()
        vals = []
        for tup in items:
            vals.append((self.fridge,) + tup)

        self.dbi.INSERT(Query.INSERT_FRIDGE_TEMP, params=vals)

    def query_insert_pour(self, pour):
        """
        @Author:        Harrison Hubbell
        @Created:       10/25/2014
        @Description:   INSERTS the pour value.
        """
        self.dbi.INSERT(Query.INSERT_POUR, params=[(pour,)])

    def query_select_current_kegs(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/04/2014
        @Description:   SELECTS current keg id
        """
        return self.dbi.SELECT(Query.SELECT_CURRENT_KEGS)

    def query_select_daily_consumption(self):
        """
        @Author:        Harrison Hubbell
        @Created:       11/09/2014
        @Description:   SELECTS aggregate daily consumption.
        """
        return self.dbi.SELECT(Query.SELECT_DAILY_CONSUMPTION)

    def query_select_fridge(self, name):
        """
        @Author:        Harrison Hubbell
        @Created:       11/07/2014
        @Description:   SELECTS fridge_id based on name.
        """
        return self.dbi.SELECT(Query.SELECT_FRIDGE_ID, params=[name])

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
    # HTTP SERVER
    # --------------------
    def handle_http_server(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @Created:       11/21/2014
        @Description:   Checks the HTTP Server process for any new messages,
                        then acts on them.
        """
        message = self.proc_poll_recv(proc_name)

        if message and message.get('type') == 'get':
            if message['data'] == 'brewers':
                brewers = list(self.dbi.SELECT(Query.SELECT_BREWERS))
                self.proc_send(proc_name, json.dumps(brewers))

            elif message['data'] == 'offering':
                params = (message['params'].get('brewer'))
                self.dbi.SELECT(Query.SELECT_BREWER_OFFERING, params=params)

        elif message and message.get('type') == 'set':
            if message['data'] == 'tap':
                params = (
                    self.fridge,
                    message['params'].get('beer_id'),
                    message['params'].get('volume')
                )
                self.dbi.INSERT(Query.INSERT_NEW_KEG, params=params)

    # --------------------
    # LED DISPLAY
    # --------------------
    def handle_led_display(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @Created:       09/10/2014
        @Description:   Tells the LED process how many rows to light.
        """
        KEG_INDEX = 0

        percent_remaining = self.kegs[KEG_INDEX]['remaining']['value']

        if percent_remaining > .75:
            rows = 4
        elif percent_remaining > .5:
            rows = 3
        elif percent_remaining > .25:
            rows = 2
        else:
            rows = 1

        self.proc_send(proc_name, rows)

    # --------------------
    # MODEL
    # --------------------
    def calculate_model(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @Created:
        @Description:   For now, it is just example data.

        """
        self.daily_consumption = [x['amount'] for x in self.query_select_daily_consumption()]
        self.proc_send(proc_name, self.daily_consumption)
        prediction = self.proc_recv(proc_name)

        for keg in self.kegs:
            keg['consumption']['days'] = prediction

        print self.kegs

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
        self.temperatures = []
        temp_vals = self.proc_poll_recv(proc_name)
        res = None

        if temp_vals:
            self.temperatures = dict(temp_vals)
            self.current_temp = sum(self.temperatures) / len(self.temperatures)
            res = True
        else:
            res = False

        return res

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

    def spawn_http_server(self, conn):
        """
        @Author:        Harrison Hubbell
        @Created:       11/21/2014
        @Description:   Create the HTTP Server process
        """
        HEADER = 'SmartkegHTTPServer'

        cfg = ConfigParser()
        cfg.read(self._CONFIG_PATH)
        host = cfg.get(HEADER, 'host')
        port = cfg.getint(HEADER, 'port')
        directory = self._BASE_DIR + 'srv/'

        server = SmartkegHTTPServer(conn, host, port, directory, logger=self.logger)
        server.main()

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
        mod = SmartkegModelMaker(conn, TimeSeriesRegression(self.TSR_PERIODS))
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

        soc = SmartkegSocketServer(conn, host, port, logger=self.logger)
        soc.set_response(soc.update_id, json.dumps(self.kegs))
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
        'TMP': 'temperature_sensor',
        'WEB': 'http_server'
    }

    smartkeg = Smartkeg()
    smartkeg.proc_add(PROC['FLO'], target=smartkeg.spawn_flow_meter, pipe=True)
    smartkeg.proc_add(PROC['LED'], target=smartkeg.spawn_led_display, pipe=True)
    smartkeg.proc_add(PROC['MOD'], target=smartkeg.spawn_model, pipe=True)
    smartkeg.proc_add(PROC['SOC'], target=smartkeg.spawn_socket_server, pipe=True)
    smartkeg.proc_add(PROC['TMP'], target=smartkeg.spawn_temp_sensor, pipe=True)
    smartkeg.proc_add(PROC['WEB'], target=smartkeg.spawn_http_server, pipe=True)
    smartkeg.proc_start_all()

    smartkeg.calculate_model(PROC['MOD'])
    smartkeg.set_datagram('kegs', smartkeg.kegs)
    smartkeg.set_datagram('temperature', smartkeg.current_temp)
    smartkeg.socket_server_set_response(PROC['SOC'], smartkeg.datagram)

    while True:
        if smartkeg.flow_meter_get_pour(PROC['FLO']):
            smartkeg.query_insert_pour(smartkeg.last_pour)
            smartkeg.set_kegs()            
            smartkeg.calculate_model(PROC['MOD'])
            smartkeg.set_datagram('kegs', smartkeg.kegs)
            smartkeg.socket_server_set_response(PROC['SOC'], smartkeg.datagram) 
            smartkeg.handle_led_display(PROC['LED'])

        if smartkeg.temperature_sensor_read(PROC['TMP']):
            smartkeg.query_insert_temperatures(smartkeg.temperatures)
            smartkeg.set_datagram('temperature', smartkeg.current_temp)
            smartkeg.socket_server_set_response(PROC['SOC'], smartkeg.datagram)

        smartkeg.handle_http_server(PROC['WEB'])

        time.sleep(0.1)
