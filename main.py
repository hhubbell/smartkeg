#!/usr/bin/env python
# ----------------------------------------------------------------------------
# Filename:     main.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Is responsible for spooling and monitoring smartkeg processes,
#               and handing data interaction between these parts.  Each
#               process that requires interaction with the database will get
#               its own connection.  This should improve performance by
#               allowing the database to manage ACID transactions.
# ----------------------------------------------------------------------------

from multiprocessing import Process, Pipe
import logging
import smartkeg
import RPi.GPIO as GPIO
import time
import json


def config(path):
    """
    @Author:        Harrison Hubbell
    @Created:       03/18/2015
    @Description:   Gathers config info and returns a serialized JSON object.
    """
    with open(path, 'r') as f:
        return json.load(f)

def db_connect(cfg):
    """
    @Author:        Harrison Hubbell
    @Created:       08/31/2014
    @Description:   Creates a database interface for inserting and
                    selecting data.
    """
    logging.info('Initializing Database Connection.')

    return smartkeg.DatabaseInterface(
        cfg['address'],
        cfg['schema'],
        cfg['user'],
        cfg['password']
    )

def start_all(procs):
    """
    @Author:        Harrison Hubbell
    @Created:       10/05/2014
    @Description:   Starts all processes in the procs list.
    """
    for proc in procs:
        proc.start()

def proc_add(target, args=None, name=None):
    """
    @Author:        Harrison Hubbell
    @Created:       10/05/2014
    @Description:   Adds a process and manages creating the pipes
                    between both nodes.  Returns a tuple of the 
                    process and pipe to that process.
    """
    if args is None: args = ()
    
    pipe_to, pipe_from = Pipe()
    args = (pipe_from,) + args

    return Process(target=target, args=args, name=name), pipe_to
    
def proc_poll_recv(node):
    """
    @Author:        Harrison Hubbell
    @created:       10/05/2014
    @Description:   Receives data from a process via its pipe without
                    blocking processing, by polling first.
    """
    if node.poll(): return node.recv()
    
def spawn_flow_meter(pipe, cfg, dbi=None):
    """
    @Author:        Harrison Hubbell
    @Created:       08/31/2014
    @Description:   Creates the Flow Meter process.
    """
    flo = smartkeg.FlowMeterController(
        cfg['pins'],
        pipe=pipe,
        dbi=dbi
    )
    flo.run()

def spawn_http_server(pipe, cfg, path, dbi=None):
    """
    @Author:        Harrison Hubbell
    @Created:       08/31/2014
    @Description:   Creates the HTTP Server process.
    """
    srv = smartkeg.HTTPServer(
        cfg['host'],
        cfg['port'],
        path,
        pipe=pipe,
        dbi=dbi
    )
    srv.set_sse_response(json.dumps({'test': 123, 'shmest': 456}))
    srv.serve_forever()

def spawn_model(pipe):
    """
    @Author:        Harrison Hubbell
    @Created:       10/07/2014
    @Description:   Creates the Modeling process.
    """
    PERIODS = 7
    
    mod = smartkeg.ModelMaker(
        smartkeg.TimeSeriesRegression(PERIODS),
        pipe,
    )
    mod.run()

def spawn_temp_sensor(pipe, cfg, dbi=None):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Creates the Temperature Sensor process.
        """
        tmp = smartkeg.TemperatureSensorController(
            cfg['sensors'],            
            cfg['directory'],
            cfg['file'],
            cfg['interval'],            
            pipe=pipe,
            dbi=dbi
        )

        tmp.run()


if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)

    CFG_PATH = '/etc/smartkeg/config.json'    
    SRV_PATH = '/srv/smartkeg/'

    cfg = config(CFG_PATH)
    #log = smartkeg.Logger(cfg['logger']['directory'], cfg['logger']['file'])
    logging.basicConfig(
        filename='{}{}.log'.format(
            cfg['logger']['directory'] + cfg['logger']['file'],
            time.strftime('%Y%m%d')
        ),
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )
    
    procs = {
        'FLO': proc_add(spawn_flow_meter, args=(cfg['flow_meter'], db_connect(cfg['database']))),
        'MOD': proc_add(spawn_model),
        'TMP': proc_add(spawn_temp_sensor, args=(cfg['temp_sensor'], db_connect(cfg['database']))),
        'WEB': proc_add(spawn_http_server, args=(cfg['server'], SRV_PATH, db_connect(cfg['database'])))
    }

    start_all([procs[x][0] for x in procs])

    while True:
        time.sleep(0.1)
