import pycom
import machine
import time
import socket
import utime
import json

import airbit



def send(url: str, time=[], temperature=0, humidity=0, pm25=0.0, pm10=0.0, northing=[], easting=[]):
    """
    Meant to send to an Flask endpoint used with the airbit_backend during testing.
    """
    if ":" in url:
        host, port = url.split(":", 1)
        port = int(port)

    ai = socket.getaddrinfo(host, port)
    ai = ai[0]
    sock = socket.socket()
    try:

        sock.connect(ai[-1])
    except OSError as err:
        print(err)
        return -1
    data = {"time": time, "temperature": temperature, "humidity": humidity,
            "pm25": pm25, "pm10": pm10, "northing": northing, "easting": easting}
    body = json.dumps(data)
    content_len = len(body)
    sock.setblocking(True)
    sock.send(
        b"POST /sensors/add HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s" % (url, content_len, body))
    sock.setblocking(False)
    print(sock.recv(4096))
    sock.close()
    return 0


def timenow():
    """Converts rtc UTC time to UTC +2"""
    utime.timezone(7200)
    return utime.localtime()


def get_coords():
    global gps
    uart = machine.UART(1, baudrate=9600, pins=("P3", "P4"))
    time.sleep(0.5)
    msg = uart.read()

    if msg:
        for item in msg:
            gps.update(chr(item))

    uart.deinit()

    return (gps.latitude_string() + gps.longitude_string())


def get_airquality():
    uart = machine.UART(1, baudrate=9600, pins=("P8", "P9"))
    time.sleep(0.5)
    ds = airbit.SDS011(uart)

    ds.read()
    uart.deinit()
    return(ds.pm25, ds.pm10)


def get_network_lte():
    """
    attaches and connects modem
    """

    lte = LTE()
    lte.attach(band=20, apn="telenor.iot")

    while not lte.isattached():
        time.sleep(0.25)
        # print(lte.send_at_cmd('AT!="fsm"'))

    lte.connect()

    while not lte.isconnected():
        time.sleep(0.25)

    return lte


pycom.heartbeat(False)
LTE = get_network_lte()
rtc = machine.RTC()
x = rtc.ntp_sync("no.pool.ntp.org")
# init GPS parser
gps = airbit.MicropyGPS()
# Init DHT sensor on Pin 21
th = airbit.DHT('P21', 1)
while 1:
    time.sleep(3)

    coords = get_coords()
    pm25, pm10 = get_airquality()
    temperature = th.read()
    # TODO(Erling) Implement telenors mqtt behaviour for MIC
    stat = send(url="51.13.36.180:8080", time=utime.gmtime, temperature=temperature.temperature,
                humidity=temperature.humidity, northing=gps.latitude, easting=gps.longitude, pm25=pm25, pm10=pm10)
