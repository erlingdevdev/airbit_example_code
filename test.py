import time
import pycom
import machine
import urequests as requests
from network import LTE
lte = LTE()
pycom.heartbeat(False)
lte.send_at_cmd('AT^RESET')
lte.send_at_cmd('AT+CFUN=0')
lte.send_at_cmd('AT+CEREG=2')
lte.send_at_cmd('AT!="clearscanconfig"')
lte.send_at_cmd('AT+CGDCONT=1,"IP","hologram"')
lte.send_at_cmd('AT+CFUN=1')
lte.attach()


def getLTE():
    if lte.isconnected():
        return lte
    if not lte.isattached():
        print('attaching ', end='')
        lte.attach()
        while not lte.isattached():
            print('.', end='')
            time.sleep(1)
    if not lte.isconnected():
        print('connnecting ', end='')
        lte.connect()
        while not lte.isconnected():
            print('.', end='')
            time.sleep(1)
    return lte


getLTE()
r = requests.urlopen('http://micropython.org/ks/test.html')
print(r.text)
lte.disconnect()
