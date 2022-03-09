import time
import airbit
import pycom


print("starting")

sds = airbit.SDS011()
gps = airbit.MicropyGPS()
dht = airbit.DHT('P21', 1)

iot = airbit.setup()

while 1:
    latitude, longitude, nmea = airbit.get_coords(gps)
    pm25, pm10 = airbit.get_airquality(sds)
    temperature, humidity = airbit.get_temphum(dht)

    print("Temperature: %s and humidity: %s" % (temperature, humidity))
    print("pm2.5: %s and pm10: %s " % (pm25, pm10))
    print("Latitude: %s and Longitude %s " % (latitude, longitude))

    airbit.send(iot, temperature=temperature, humidity=humidity,
                latitude=latitude, longitude=longitude, pm10=pm10, pm25=pm25, )

    time.sleep(10)
