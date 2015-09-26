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

def model(data):
    """
    @Author:        Harrison Hubbell
    @Created:       08/17/2015
    @Description:   Generate a new time series regression model
    """
    PERIODS = 7
    
    reg = smartkeg.TimeSeriesRegression(PERIODS)
    forecast = reg.forecast(data)

    logging.info('New Model: {}'.format(str(reg)))
    logging.info('New Forecast: {}'.format(forecast))

    return forecast

def start(*procs):
    """
    @Author:        Harrison Hubbell
    @Created:       10/05/2014
    @Description:   Starts all processes supplied.
    """
    for proc in procs:
        proc.start()

def proc(target, args=None, name=None):
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
    
def spawn_flow_meter(pipe, cfg, dbi=None):
    """
    @Author:        Harrison Hubbell
    @Created:       08/31/2014
    @Description:   Creates the Flow Meter process.
    """
    flo = smartkeg.FlowMeterManager(
        cfg['pins'],
        pipe=pipe,
        dbi=dbi
    )
    flo.run()

def spawn_temp_sensor(pipe, cfg, dbi=None):
        """
        @Author:        Harrison Hubbell
        @Created:       08/31/2014
        @Description:   Creates the Temperature Sensor process.
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
            'consumption': [[0, 5], [1, 7], [2, 9], [3,1], [4,3], [5, 6], [6, 13], [2, 2], [3,4], [4,10]]
        },
        {
            'name': 'Fiddlehead IPA',
            'brand': 'Fiddlehead',
            'abv': 4.5,
            'ibu': 'NA',
            'rating': 3,
            'remaining': .19,
            'consumption': [[0, 1], [1, 8], [2, 2], [3,4], [4,10]]
        },
        {
            'name': 'Cone Head',
            'brand': 'Zero Gravity',
            'abv': 4.5,
            'ibu': 'NA',
            'rating': 3,
            'remaining': .7865,
            'consumption': [[0, 1], [1, 8], [2, 2], [3,4], [4,9]]
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
            'consumption': [[0, 1], [1, 8], [2, 2], [4,3], [5, 6], [6, 13], [2, 2], [4,10]]
    }

    cfg = config(CFG_PATH)

    logging.basicConfig(
        filename='{}{}.log'.format(
            cfg['logger']['directory'] + cfg['logger']['file'],
            time.strftime('%Y%m%d')
        ),
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )
    logging.info('Starting the Smartkeg system')
    
    db = db_connect(cfg['database'])
    
    serving = TESTDF#db.select(*smartkeg.query.get_now_serving())
    temperature = db.select(*smartkeg.query.get_fridge_temp(cfg['fridge'].items()))

    http = smartkeg.HTTPServerManager(
        cfg['server']['host'],
        cfg['server']['port'],
        SRV_PATH,
        dbi=db_connect(cfg['database'])
    )
    http.sse_response(json.dumps(serving))
    http.start()

    flowproc, flowpipe = proc(spawn_flow_meter, args=(cfg['flow_meter'], db_connect(cfg['database'])))
    tempproc, temppipe = proc(spawn_temp_sensor, args=(cfg['temp_sensor'], db_connect(cfg['database'])))

    start(flowproc, tempproc)

    while True:
        if flowpipe.poll():
            serving = db.select(*smartkeg.query.get_now_serving())

        if temppipe.poll():
            temperature = db.select(*smartkeg.query.get_fridge_temp(cfg['fridge'].items()))
            
        for i, beer in enumerate(serving):
            #subtract a little beer
            beer['remaining'] -= .001

            if beer['remaining'] < 0:
                serving[i] = dict(REPLF)

        http.sse_response(json.dumps(serving))
        time.sleep(1)
        #time.sleep(0.1)
