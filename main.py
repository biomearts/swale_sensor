#!/usr/bin/env python3

import time, json, math, threading, queue, requests, os
from random import random
from collections import deque, OrderedDict
from housepy import config, log, util, process
from housepy.xbee import XBee
from weather_station import WeatherStation
import remote_sensors

process.secure_pid(os.path.abspath(os.path.join(os.path.dirname(__file__), "run")))

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
                response = requests.post(config['server'], json=data, timeout=5)
                log.info(response.status_code)
            except Exception as e:
                log.error(log.exc(e))

data_sender = DataSender()
remote_sensors.data_sender = data_sender
weather_station = WeatherStation(data_sender)

while True:
    time.sleep(1)
