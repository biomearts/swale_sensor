#!/usr/bin/env python3

import time, json, math, threading, queue, requests, os
from random import random
from collections import deque, OrderedDict
from housepy import config, log, util, process
from housepy.xbee import XBee

RANGE = 0, 1023
TYPE = "moisture"

data_sender = None

def message_handler(response):
    try:
        # print(response['sensor'], response['samples'], response['rssi'])
        t_utc = util.timestamp()
        sensor = response['sensor']
        sample = response['samples']
        rssi = response['rssi']
        data = {'t_utc': t_utc, 'type': TYPE, 'sensor': sensor, 'sample': sample, 'rssi': rssi}
        data.update({'value': max(data['sample'][0], RANGE[0]) / RANGE[1]})
        del data['sample']
        log.info(json.dumps(data, indent=4))
        if data_sender is not None:
            data_sender.queue.put(data)
    except Exception as e:
        log.error(log.exc(e))

xbee = XBee(config['device_name'], message_handler=message_handler, blocking=False, verbose=False)

if __name__ == "__main__":
    while True:
        time.sleep(0.1)
