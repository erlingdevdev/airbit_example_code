import sds011
import pycom
import machine
import time
from gps import MicropyGPS
from dht import DHT
import utime
import json
from telenor import StartIoT

pycom.heartbeat(False)


def timenow():
    """Converts rtc UTC time to UTC +2"""
    utime.timezone(7200)
    return utime.localtime()


def get_coords():
    global gps
    uart = machine.UART(1, baudrate=9600, pins=("P3", "P4"))
    time.sleep(0.5)
    # TODO(Erling) timeout mechanism
    msg = uart.read()
    print(msg)

    if msg:
        for item in msg:
            gps.update(chr(item))

    uart.deinit()

    return (gps.latitude_string() + gps.longitude_string())


def get_airquality():
    uart = machine.UART(1, baudrate=9600, pins=("P8", "P9"))
    time.sleep(0.5)
    ds = sds011.SDS011(uart)

    ds.read()
    uart.deinit()
    return (ds.pm25, ds.pm10)


try:
    iot = StartIoT(network='lte-m')
    iot.connect()
except Exception as e:
    print(e)


try:
    rtc = machine.RTC()
    rtc.ntp_sync("no.pool.ntp.org")
except Exception as e:
    print("errpr")

# init GPS parser
gps = MicropyGPS()
# Init DHT sensor on Pin 21
th = DHT('P21', 1)

# TODO(Erling) SD kor:t
while 1:
    # pycom.rgbled(0xffffff)
    # time.sleep(3)
    # pycom.rgbled(0x0)

    try:
        coords = get_coords()
        pm25, pm10 = get_airquality()
        temperature = th.read()
    except Exception as e:
        print(e, "got error")
        pycom.rgbled(0xff0000)
        machine.reset()

    payload = {
        'temperature': temperature.temperature,
        'humidity': temperature.humidity,
        'Location': coords,
        'Pm25': pm25,
        'Pm10': pm10,
    }
    js = json.dumps(payload)
    print(js)
    print(coords)
    if coords == "0° 0.0' N0° 0.0' W":
        pycom.rgbled(0xf00000)
    else:
        pycom.rgbled(0xffffff)

    try:

        iot.send(js)
    except Exception as e:
        pycom.rgbled(0xff0000)
        time.sleep(2)
        pycom.rgbled(0x0)
        print("could not send, %s" % (e))
    # Publish JSON string over the network
