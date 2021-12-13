import time
import airbit


def run():
    sds = airbit.SDS011()
    gps = airbit.MicropyGPS()
    dht = airbit.DHT('P21', 1)
    iot = airbit.setup()

    while 1:
        latitude, longitude = airbit.get_coords(gps)
        pm25, pm10 = airbit.get_airquality(sds)
        temperature, humidity = airbit.get_temphum(dht)

        airbit.send(iot, temperature=temperature,
                    humidity=humidity, latitude=latitude, longitude=longitude, pm10=pm10, pm25=pm25)
        time.sleep(60)


if __name__ == "__main__":

    run()
