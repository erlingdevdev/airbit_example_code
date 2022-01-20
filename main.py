import time
import airbit
import uos
# import sqnsupgrade

# print(uos.uname(), sqnsupgrade.info())


def run():
    # sds = airbit.SDS011()
    # gps = airbit.MicropyGPS()
    # dht = airbit.DHT('P21', 1)
    iot = airbit.setup(debug=0)

   # while 1:
    #     latitude, longitude = airbit.get_coords(gps)
    #     pm25, pm10 = airbit.get_airquality(sds)
    #     temperature, humidity = airbit.get_temphum(dht)
    #     print(temperature, humidity, pm10, pm25, latitude, longitude)
    #     airbit.send(iot, temperature=temperature,
    #                 humidity=humidity, latitude=latitude, longitude=longitude, pm10=pm10, pm25=pm25)
    #     time.sleep(1)


if __name__ == "__main__":

    run()

"""
<< < Welcome to the SQN3330 firmware updater[1.2.6] >> >
>> > GPy with firmware version 1.20.2.r6
Your modem is in application mode. Here is the current version:
UE5.0.0.0d
LR5.1.1.0-43818

IMEI: 354347095149339
(sysname='GPy', nodename='GPy', release='1.20.2.r6', version='v1.11-c5a0a97 on 2021-10-28', machine='GPy with ESP32', pybytes='1.7.1') None
"""
