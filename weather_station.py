#!/usr/bin/env python3

import serial, json, threading, time
from housepy import config, log, util

TYPE = "weather"

class WeatherStation(threading.Thread):

    def __init__(self, data_sender=None):
        threading.Thread.__init__(self)
        self.daemon = True
        self.data_sender = data_sender
        self.start()

    def run(self):
        try:
            connection = serial.Serial("/dev/tty.usbmodem1D11321", 9600)
        # if device_name is None:
        #     for dn in os.listdir("/dev"):
        #         if "tty.usbserial-" in dn:
        #             device_name = os.path.join("/dev", dn)
        #             break
        #         if "ttyUSB" in dn:
        #             device_name = os.path.join("/dev", dn)
        #             break
        #     if device_name is None:
        #         log.info("No devices available")
        #         exit()
        # log.info("Receiving xbee messages on %s" % device_name)

        except Exception as e:
            log.error(log.exc(e))
        else:
            while True:
                result = None
                try:
                    result = connection.readline().decode('utf-8').strip()
                    data = json.loads(result)
                    data.update({'t_utc': util.timestamp(), 'type': TYPE})                    
                    log.info(json.dumps(data, indent=4))
                    if self.data_sender is not None:
                        self.data_sender.queue.put(data)
                except Exception as e:
                    log.error(log.exc(e))
                    log.info(result)

if __name__ == "__main__":
    weather_station = WeatherStation()
    while True:
        time.sleep(0.1)