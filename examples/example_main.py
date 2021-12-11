
import pycom
import machine

import airbit

pycom.heartbeat(False)

def run():

    sds = airbit.SDS011()
    gps = airbit.MicropyGPS()
    dht = airbit.DHT('P21', 1)
    iot = airbit.setup()

    rtc = machine.RTC()
    x = rtc.ntp_sync("no.pool.ntp.org")

    while 1:
        coords = airbit.get_coords(gps)
        pm25, pm10 = airbit.get_airquality(sds)
        temperature, humidity = airbit.get_temphum(dht)

        airbit.send(iot, temperature=temperature,
                    humidity=humidity, coords=coords, pm10=pm10, pm25=pm25)


if __name__ == "__main__":

    run()
