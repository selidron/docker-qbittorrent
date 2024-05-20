#!/usr/bin/python3

import time
import os
from threading import Thread

from qbt import QBt

def main(file, sleep_time):
    while True:
        try:
            qbt = QBt()
            print('API loaded.')
            break
        except:
            time.sleep(3)

    while True:
        port = int(open(file, 'r').read())
        qbt.set_port(port)

        time.sleep(sleep_time)

gluetun_file = '/config/gluetun/forwarded_port'
check_time = 60 * 60 * 3 if not os.environ['port_check_interval'] else os.environ['port_check_interval']

thread = Thread(target=main, args=[gluetun_file, check_time])
print('Launching Port Manager thread...')
thread.run()