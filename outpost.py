#!/usr/bin/env python3

import time, json, math, threading, queue, requests, os
from random import random
from collections import deque, OrderedDict
from housepy import config, log, util, process
from housepy.xbee import XBee

RANGE = 0, 1023
SOURCE = "outpost"

data_sender = None

def message_handler(response):
    try:
        # print(response['number'], response['samples'], response['rssi'])
        # t_utc = util.timestamp()      ## let server supply time
        number = response['sensor']
        sample = response['samples']
        rssi = response['rssi']
        data = {'source': SOURCE, 'number': number, 'sample': sample, 'rssi': rssi}
        data.update({'moisture': max(data['sample'][0], RANGE[0]) / RANGE[1]})
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
