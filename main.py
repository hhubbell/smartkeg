#!/usr/bin/env python2
# ----------------------------------------------------------------------------
# Filename:     main.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Is responsible for spooling and monitoring smartkeg processes,
#               and handing data interaction between these parts.
# ----------------------------------------------------------------------------

from ConfigParser import ConfigParser
from multiprocessing import Process, Pipe
import smartkeg
import RPi.GPIO as GPIO
import time
import json
import os

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
    LOGGER.log('Initializing Database Connection.')

    return smartkeg.DatabaseInterface(
        cfg['address'],
        cfg['schema'],
        cfg['user'],
        cfg['password'],
        logger=LOGGER
    )

def proc_add(target, args=None, name=None):
    """
    @Author:        Harrison Hubbell
    @Created:       10/05/2014
    @Description:   Adds a process and manages creating the pipes
                    between both nodes.
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
    
def spawn_flow_meter(pipe, cfg, logger=None, dbi=None):
    """
    @Author:        Harrison Hubbell
    @Created:       08/31/2014
    @Description:   Creates the Flow Meter process.
    """
    flo = smartkeg.FlowMeterController(
        cfg['pin'],
        pipe=pipe,
        dbi=dbi,
        logger=logger
    )
    flo.run()

def spawn_http_server(pipe, cfg, path, logger=None, dbi=None):
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
        dbi=dbi,
        logger=logger
    )
    srv.serve_forever()

def spawn_temp_sensor(pipe, cfg, logger=None, dbi=None):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Creates the Temperature Sensor process.
        """
        tmp = smartkeg.TemperatureSensorReader(
            cfg['interval'],
            cfg['directory'],
            cfg['file'],
            cfg['sensors'],
            pipe=pipe,
            dbi=dbi,
            logger=logger
        )

        tmp.run()


if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)

    CFG_PATH = '/etc/smartkeg/config.json'    
    SRV_PATH = '/srv/smartkeg/'
    TSR_PERIODS = 7

    cfg = config(CFG_PATH)  
    log = smartkeg.Logger(cfg['logger'])
    
    procs = {
        'FLO': proc_add(spawn_flow_meter, args=(cfg['flow_meter'], log)),
        'MOD': 'model',
        'SOC': 'socket_server',
        'TMP': proc_add(spawn_temperature_sensor, args=(cfg['temp_sensor'], log)),
        'WEB': proc_add(spawn_http_server, args=(cfg['server'], SRV_PATH, log))
    }
