from GPS import MicropyGPS
import pycom
import machine
import time
import utime
import gc
from network import LTE
import sds011
from dht import DHT

from machine import SPI, Pin, UART

# boolean to choose whether to use SD card or pybytes
PYBYTES = True


class Airbit():
    def __init__(self):
        self.gps = MicropyGPS()
        self.sds011 = None
        self._lte = None
        self._dht11 = None
        self._rtc = None
        self.media = PYBYTES
        self.pybytes_enabled = False
        self.pybytes_isinit()

        self.GPS_PINS = ("P3", "P4")
        self.SDS011_PINS = ("P6", "P7")
        self.SDCARD_PINS = ("P10", "P11", "P14")
        self.DHT11_PIN = "P8"
        self.init_sensors()

    def init_sensors(self):
        self.dht11()
        self.wrtc()
        self.lte()

    def pybytes_isinit(self):
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
        if result.is_valid():
            self.write_to_media([0, 1], [result.temperature, result.humidity])
        # pycom.rgbled(0xF800)

    def do_airquality(self):
        """
        Initalises UART, does operation and deinitialises the bus again, so its ready to be used by gps 
        """
        uart = UART(1, baudrate=9600, pins=self.SDS011_PINS)
        self.sds011 = sds011.SDS011(uart)
        self.sds011.read()
        uart.deinit()
        self.write_to_media([4, 5], [self.sds011.pm25, self.sds011.pm10])
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
            self.write_to_media(
                [2, 3], [self.gps.latitude, self.gps.longitude])
        # pycom.rgbled(0xFFE0)
        return self.gps.latitude, self.gps.longitude

    def wrtc(self):
        # set wireless rtc (ntp)
        if not self._rtc:
            self._rtc = machine.RTC()
            self._rtc.ntp_sync("pool.ntp.org")
            print('\nRTC Set from NTP to UTC:', self._rtc.now())
            return self._rtc

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
    unit = Airbit()

    while 1:
        unit.do_airquality()
        time.sleep(3)
        unit.do_gps()
        time.sleep(3)
        unit.do_temperature()
        time.sleep(10)


main()
