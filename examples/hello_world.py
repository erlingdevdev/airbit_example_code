import pycom
from time import sleep


pycom.rgbled(0xffff00)
sleep(2)
pycom.rgbled(0x0)
