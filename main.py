#!/usr/bin/env python3

import time, json, math, threading, queue, requests
from random import random
from collections import deque, OrderedDict
from housepy import config, log, util
from housepy.xbee import XBee

RANGE = 0, 1023
TYPE = "moisture"

def message_handler(response):
    try:
        # print(response['sensor'], response['samples'], response['rssi'])
        t_utc = util.timestamp(ms=True)        
        sensor = response['sensor']
        sample = response['samples']
        rssi = response['rssi']
        data = {'t_utc': t_utc, 'type': TYPE, 'sensor': sensor, 'sample': sample, 'rssi': rssi}
        data_sender.queue.put(data)
    except Exception as e:
        log.error(log.exc(e))


class DataSender(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = queue.Queue()
        self.start()

    def run(self):
        while True:
            try:
                data = self.queue.get()
                value = max(data['sample'][0], RANGE[0]) / RANGE[1]
                entry = {'t_utc': util.timestamp(), 'sensor': data['sensor'], 'type': TYPE, 'value': value, 'rssi': data['rssi']}
                log.info(json.dumps(entry, indent=4))
                response = requests.post(config['server'], json=entry, timeout=5)
                log.info(response.status_code)
            except Exception as e:
                log.error(log.exc(e))


data_sender = DataSender()
xbee = XBee(config['device_name'], message_handler=message_handler, blocking=True, verbose=True)
