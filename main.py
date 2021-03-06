#!/usr/bin/env python
#
# Filename:     main.py
# Author:       Harrison Hubbell
# Date:         08/31/2014
# Description:  Is responsible for spooling and monitoring smartkeg
#               processes, and handing data interaction between these parts.
#

from multiprocessing import Process, Pipe
import logging
import smartkeg
import RPi.GPIO as GPIO
import time
import json


def config(path):
    """
    @author:        Harrison Hubbell
    @created:       03/18/2015
    @description:   Reads config info and returns a serialized JSON object.
    """
    with open(path, 'r') as f:
        return json.load(f)

def dbconnect(cfg):
    """
    @author:        Harrison Hubbell
    @created:       08/31/2014
    @description:   Creates a database interface for inserting and
                    selecting data.
    """
    logging.info('Initializing Database Connection.')

    return smartkeg.DatabaseInterface(
        cfg['address'],
        cfg['schema'],
        cfg['user'],
        cfg['password']
    )

def model(data):
    """
    @author:        Harrison Hubbell
    @created:       08/17/2015
    @description:   Generate a new time series regression model
    """
    PERIODS = 7

    reg = smartkeg.TimeSeriesRegression(PERIODS)
    forecast = reg.forecast(data)

    logging.info('New Model: %s', str(reg))
    logging.info('New Forecast: %s', forecast)

    return forecast

def start(*procs):
    """
    @author:        Harrison Hubbell
    @created:       10/05/2014
    @description:   Starts all processes supplied.
    """
    for proc in procs:
        proc.start()

def proc(target, args=None, name=None):
    """
    @author:        Harrison Hubbell
    @created:       10/05/2014
    @description:   Adds a process and manages creating the pipes
                    between both nodes.  Returns a tuple of the
                    process and pipe to that process.
    """
    if args is None: args = ()

    pipe_to, pipe_from = Pipe()
    args = (pipe_from,) + args

    return Process(target=target, args=args, name=name), pipe_to

def spawn_flow_meter(pipe, cfg, dbi=None):
    """
    @author:        Harrison Hubbell
    @created:       08/31/2014
    @description:   Creates the Flow Meter process.
    """
    flo = smartkeg.FlowMeterManager(
        cfg['pins'],
        pipe=pipe,
        dbi=dbi
    )
    flo.run()

def spawn_temp_sensor(pipe, cfg, dbi=None):
    """
    @author:        Harrison Hubbell
    @created:       08/31/2014
    @description:   Creates the Temperature Sensor process.
    """
    tmp = smartkeg.TemperatureSensorManager(
        cfg['interval'],
        sensors=cfg['sensors'],
        pipe=pipe,
        dbi=dbi
    )

    tmp.run()


if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)

    CFG_PATH = '/etc/smartkeg/config.json'
    SRV_PATH = '/srv/smartkeg/'

    # Test data frame
    TESTDF = [
        {
            'name': 'Bud Light',
            'brand': 'Budweiser',
            'abv': 4.5,
            'ibu': 'NA',
            'rating': 3,
            'remaining': .34,
            'consumption': [
                [0, 5], [1, 7], [2, 9], [3, 1], [4, 3],
                [5, 6], [6, 13], [2, 2], [3, 4], [4, 10]
            ]
        },
        {
            'name': 'Fiddlehead IPA',
            'brand': 'Fiddlehead',
            'abv': 4.5,
            'ibu': 'NA',
            'rating': 3,
            'remaining': .19,
            'consumption': [[0, 1], [1, 8], [2, 2], [3, 4], [4, 10]]
        },
        {
            'name': 'Cone Head',
            'brand': 'Zero Gravity',
            'abv': 4.5,
            'ibu': 'NA',
            'rating': 3,
            'remaining': .7865,
            'consumption': [[0, 1], [1, 8], [2, 2], [3, 4], [4, 9]]
        },
        {
            'name': 'Hodad',
            'brand': 'Fiddlehead',
            'abv': 4.5,
            'ibu': 'NA',
            'rating': 3,
            'remaining': .365,
            'consumption': [[0, 1], [1, 3], [2, 4], [3, 6], [4, 8]]
        }
    ]

    # Replacement beer when other hits 0
    REPLF = {
        'name': 'Baltic Porter',
        'brand': 'Smuttynose',
        'abv': 9.9,
        'ibu': 'NA',
        'rating': 5,
        'remaining': 1,
        'consumption': [
            [0, 1], [1, 8], [2, 2], [4, 3],
            [5, 6], [6, 13], [2, 2], [4, 10]
        ]
    }

    cfg = config(CFG_PATH)
    fridge = cfg['fridge']
    dbconf = cfg['database']

    logging.basicConfig(
        filename='{}{}.log'.format(
            cfg['logger']['directory'] + cfg['logger']['file'],
            time.strftime('%Y%m%d')
        ),
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )
    logging.info('Starting the Smartkeg system')


    db = dbconnect(dbconf)

    with db as d:
        srv = TESTDF#d.select(*smartkeg.query.get_now_serving())
        tmp = d.select(*smartkeg.query.get_fridge_temp(fridge.items()))

    http = smartkeg.HTTPServerManager(
        cfg['server']['host'],
        cfg['server']['port'],
        SRV_PATH,
        dbi=dbconnect(dbconf)
    )
    http.sse_response(json.dumps(srv))
    http.start()

    flowproc, flowpipe = proc(
        spawn_flow_meter,
        args=(cfg['flow_meter'], dbconnect(dbconf))
    )

    tempproc, temppipe = proc(
        spawn_temp_sensor,
        args=(cfg['temp_sensor'], dbconnect(dbconf))
    )

    start(flowproc, tempproc)

    while True:
        if flowpipe.poll():
            with db as d:
                srv = d.select(*smartkeg.query.get_now_serving())

        if temppipe.poll():
            with db as d:
                tmp = d.select(*smartkeg.query.get_fridge_temp(fridge.items()))

        for i, beer in enumerate(srv):
            #subtract a little beer
            beer['remaining'] -= .001

            if beer['remaining'] < 0:
                srv[i] = dict(REPLF)

        http.sse_response(json.dumps(srv))
        time.sleep(1)
        #time.sleep(0.1)
