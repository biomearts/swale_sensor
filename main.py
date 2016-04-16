#!/usr/bin/env python3

import time, json, math, threading, queue
from random import random
from collections import deque, OrderedDict
from housepy import config, log, util, net
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
            data = []
            try:
                start_t = time.time()
                while True:
                    data.append(self.queue.get_nowait())
            except queue.Empty:
                if len(data):
                    ## doesnt take into account multiple sensors
                    average_sample = round(sum([d['sample'][0] for d in data]) / len(data)) / RANGE[-1]
                    average_rssi = round(sum([d['rssi'] for d in data]) / len(data))
                    entry = {'t_utc': util.timestamp(), 'type': TYPE, 'moisture': average_sample, 'rssi': average_rssi}
                    log.info(json.dumps(entry, indent=4))
                    try:
                        net.read(config['server'], data=entry, timeout=5)
                    except Exception as e:
                        log.error(log.exc(e))
            while time.time() - start_t < 5.0:
                time.sleep(0.02)


data_sender = DataSender()
xbee = XBee(config['device_name'], message_handler=message_handler, blocking=True)
