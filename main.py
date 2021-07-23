import sds011
import pycom
import os
from machine import SPI, Pin, UART
import sdcard
import time
from GPS import MicropyGPS
from dht import DHT


def _sdcard():

    spi = SPI(0, mode=SPI.MASTER, baudrate=1000000,
              polarity=0, phase=0, pins=("P10", "P11", "P14"))

    cs = Pin('P9')
    sd = sdcard.SDCard(spi, cs)
    return sd


def get_coords():
    global gps
    uart = UART(1, baudrate=9600, pins=("P3", "P4"))
    time.sleep(0.5)
    msg = uart.readall()
    for item in msg:
        gps.update(chr(item))

    uart.deinit()

    return (gps.latitude_string() + gps.longitude_string())


def get_airquality():
    uart = UART(1, baudrate=9600, pins=("P6", "P7"))
    time.sleep(0.5)
    ds = sds011.SDS011(uart)

    ds.read()
    uart.deinit()
    return(ds.pm25, ds.pm10)


pycom.heartbeat(False)

# init GPS parser
gps = MicropyGPS()
# Init DTH sensor on Pin 8
th = DTH('P8', 0)

sd = _sdcard()
os.mount(sd, "/sd")

with open("/sd/log.txt", "a") as f:
    while 1:
        time.sleep(3)
        # hent ut gps koordinater
        string = get_coords()

        pm25, pm10 = get_airquality()

        result = th.read()
        try:
            f.write(string + " ")
            f.write(str(result.temperature) + " ")
            f.write(str(result.humidity) + " ")
            f.write(str(pm25) + " ")
            f.write(str(pm10))
            f.write("\r\n")
            pycom.rgbled(0xff00)
            time.sleep(0.5)
            pycom.rgbled(0x0)
        except Exception:
            pycom.rgbled(0x7f0000)
            time.sleep(0.5)
            pycom.rgbled(0x0)
