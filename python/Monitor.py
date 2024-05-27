#!/usr/bin/python3

import time
import os
import signal
from threading import Thread

from qbt import QBt
from ClamAV import update as update_clamAV

class Monitor:
    alive = True
    timer = 60 * 60 * 3
    def __init__(self) -> None:
        signal.signal(signal.SIGINT, self.kill)
        signal.signal(signal.SIGTERM, self.kill)
    
    def run(self):
        while True:
            try:
                qbt = QBt()
                print('API Loaded.')
                break
            except:
                time.sleep(3)

        print('Launching Port Monitor...')

        while Monitor.alive:
            # Update port number
            port = int(open(gluetun_file, 'r').read())
            qbt.set_port(port)

            # Check for ClamAV Database Updates
            update_clamAV()

            time.sleep(Monitor.timer)
    
    def set_time(self, time):
        if time and ((isinstance(time, int) and time > 60) or (isinstance(time, str) and time.isnumeric and int(time) > 60)):
            print(f'Setting port monitor interval to {time} secs.')
            self.timer = time
        else:
            print(f'Invalid time: {type(time)}({time})')
    
    def kill(self):
        self.alive = False

gluetun_file = os.environ['gluetun_port_file']
Monitor = Monitor()
Monitor.set_time(os.environ['port_check_interval'])

thread = Thread(target=Monitor.run)