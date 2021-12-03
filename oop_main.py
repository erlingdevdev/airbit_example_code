import utime
from GPS import MicropyGPS
import machine
import time
from network import LTE
import sds011
from dht import DHT
import socket
from machine import UART
import pycom

# boolean to choose whether to use SD card or pybytes
PYBYTES = 1

"""
Old version but with class implementation, was used for alpha testing
"""


def send(url: str, time=[], temperature=0, humidity=0, pm25=0.0, pm10=0.0, northing=[], easting=[]):

    import json
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
    print(body, content_len, type(body))
    sock.setblocking(True)
    sock.send(
        b"POST /sensors/add HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s" % (url, content_len, body))
    sock.setblocking(False)
    print(sock.recv(4096))
    sock.close()
    return 0


class Airbit():

    def __init__(self):
        self.gps = MicropyGPS()
        self.sds011 = None
        self._lte = None
        self._dht11 = None
        self._rtc = None
        self.pybytes_enabled = False
        self.pybytes_isinit()
        self.SDS011_PINS = ("P2", "P3")
        self.GPS_PINS = ("P22", "P23")
        self.SDCARD_PINS = ("P10", "P11", "P14")
        self.DHT11_PIN = "P11"
        self.init_sensors()

    def init_sensors(self):
        self.dht11()
        self.wrtc()

        self.lte()

    def pybytes_isinit(self):
        if PYBYTES:
            if 'pybytes' in globals():
                if pybytes.isconnected():
                    self.pybytes_enabled = True

    def dht11(self):
        # temperature sensor initialisation
        if not self._dht11:
            self._dht11 = DHT(self.DHT11_PIN, 0)
            return self._dht11

    def do_temperature(self):
        # reads value from sensor, and sends to pybytes.
        result = self._dht11.read()
        print(result.temperature, result.humidity)
        if result.is_valid():
            if PYBYTES:
                self.write_to_media(
                    [0, 1], [result.temperature, result.humidity])

            return result.temperature, result.humidity
        # pycom.rgbled(0xF800)

    def do_airquality(self):
        """
        Initalises UART, does operation and deinitialises the bus again, so its ready to be used by gps
        """
        uart = UART(1, baudrate=9600, pins=self.SDS011_PINS)
        self.sds011 = sds011.SDS011(uart)
        err = self.sds011.read()

        uart.deinit()
        if not err:
            return 0.0, 0.0
        if PYBYTES:
            self.write_to_media([4, 5], [self.sds011.pm25, self.sds011.pm10])

        return self.sds011.pm25, self.sds011.pm10

        # pycom.rgbled(0xFF00)

    def do_gps(self):
        """
        Initalises UART, does operation and deinitialises the bus again, so its ready to be used by sds011
        """
        uart = UART(1, baudrate=9600, pins=self.GPS_PINS)
        time.sleep(0.5)
        msg = uart.read()
        if msg:
            for item in msg:
                self.gps.update(chr(item))

        uart.deinit()
        if msg:
            if PYBYTES:
                self.write_to_media(
                    [2, 3], [self.gps.latitude, self.gps.longitude])
        # pycom.rgbled(0xFFE0)
        return self.gps.latitude, self.gps.longitude

    def wrtc(self):
        # set wireless rtc (ntp) RTC keeps track of time
        if not self._rtc:
            self._rtc = machine.RTC()
            self._rtc.ntp_sync("no.pool.ntp.org")
            # print('\nRTC Set from NTP to UTC:', self._rtc.now())
            return self._rtc

    def timenow(self):
        """Converts rtc UTC time to UTC +2"""
        utime.timezone(7200)
        return utime.localtime()

    def lte(self):
        if not self._lte:
            self._lte = LTE()
            self.get_network_lte()

    def get_network_lte(self):
        """
        attaches and connects modem
        """
        self._lte.attach(band=20, apn="telenor.iot")
        while not self._lte.isattached():
            time.sleep(0.25)

            print('.', end='')
            # get the System FSM
            print(self._lte.send_at_cmd('AT!="fsm"'))

        print("attached!")
        self._lte.connect()

        while not self._lte.isconnected():
            time.sleep(0.25)
            print('#', end='')
            print(self._lte.send_at_cmd('AT!="fsm"'))
        print("] connected!")

        return self._lte

    def write_to_media(self, signals: list, arguments: list):
        # Function to send one value to one signal,
        print(arguments, signals)
        pycom.rgbled(0xffffff)
        time.sleep(0.5)
        pycom.rgbled(0x000000)
        if PYBYTES:
            if self.pybytes_enabled:
                for i, val in enumerate(arguments):
                    pybytes.send_signal(signals[i], val)

    def lte_deattach(self):
        if self._lte.isattached():
            self._lte.dettach()

    def lte_disconnect(self):
        if self._lte.isconnected():
            self._lte.disconnect()


def main():
    pycom.heartbeat(False)
    pycom.rgbled(0xF0FF02)
    unit = Airbit()
    time.sleep(5)
    while 1:
        if PYBYTES:
            # heartbeat
            unit.write_to_media([6], [1])
        try:
            # pm25, pm10 = unit.do_airquality()
            # northing, easting = unit.do_gps()
            temp, humidity = unit.do_temperature()
            print(temp, humidity, pm25, pm10, northing, easting)
        except:
            pycom.rgbled(0xff00ff)
            time.sleep(0.5)
            pycom.rgbled(0x000000)
        time.sleep(10)
        if not PYBYTES:
            stat = send(url="51.107.210.9:8080", time=unit.timenow(), temperature=temp, humidity=humidity,
                        northing=northing, easting=easting, pm25=pm25, pm10=pm10)
            if stat < 0:
                time.sleep(10)


# main()
pycom.heartbeat(False)
while 1:
    pycom.rgbled(0xffff00)

    time.sleep(1)
    pycom.rgbled(0xff0000)
    time.sleep(1)
    pycom.rgbled(0x000000)
    time.sleep(2)
