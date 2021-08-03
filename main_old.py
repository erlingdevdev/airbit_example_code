#!/usr/bin/env python
#
# Copyright (c) 2020, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

import pycom
import machine
import time
import utime
import gc
from network import LTE
from GPS import MicropyGPS
import sds011
from dht import DHT

from machine import SPI, Pin, UART


def get_coords():
    global gps

    uart = UART(1, baudrate=9600, pins=("P3", "P4"))
    time.sleep(0.5)
    msg = uart.read()
    print(msg)
    try:
        for item in msg:
            gps.update(chr(item))
    except:
        return (0, 0)
    uart.deinit()
    return (gps.latitude, gps.longitude)


def get_airquality():
    uart = UART(1, baudrate=9600, pins=("P6", "P7"))
    time.sleep(0.5)
    ds = sds011.SDS011(uart)

    ds.read()
    uart.deinit()
    return(ds.pm25, ds.pm10)


lte = LTE()
gc.enable()
lte.attach(band=20, apn="telenor.iot")
print("attaching..", end='')
while not lte.isattached():
    time.sleep(0.25)

    print('.', end='')
    print(lte.send_at_cmd('AT!="fsm"'))         # get the System FSM
print("attached!")
lte.connect()
while not lte.isconnected():
    time.sleep(0.25)
    print('#', end='')
    print(lte.send_at_cmd('AT!="fsm"'))
print("] connected!")

th = DHT('P8', 0)
gps = MicropyGPS()
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')


pybytes_enabled = False
if 'pybytes' in globals():
    if(pybytes.isconnected()):
        print('Pybytes is connected, sending signals to Pybytes')
        pybytes_enabled = True

pycom.heartbeat(False)
while (True):
    pycom.rgbled(0xffff00)

    #f.write("{} - {}\n".format(coord, rtc.now()))
    coords = get_coords()
    pm25, pm10 = get_airquality()
    print(pm25, pm10)
    result = th.read()
    if(pybytes_enabled):
        pycom.rgbled(0xff00)           # turn on the RGB LED in green colour

        if coords[0]:
            print("{} - {} - {} - {}".format(coords[0],
                                             coords[1], rtc.now(), gc.mem_free()))
            pybytes.send_signal(1, coords)
        pybytes.send_signal(3, (pm25, pm10))
        if result.is_valid():
            pybytes.send_signal(4, (result.temperature, result.humidity))
