
import socket

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




def run():

    sds = airbit.SDS011()
    gps = airbit.MicropyGPS()
    dht = airbit.DHT('P21', 1)

    while 1:
        coords = airbit.get_coords(gps)
        pm2, pm10 = airbit.get_airquality(sds)
        dht = airbit.get_temphum(dht)

        stat = send(url="51.13.36.180:8080", time=utime.gmtime, temperature=temperature.temperature,
                humidity=temperature.humidity, northing=gps.latitude, easting=gps.longitude, pm25=pm25, pm10=pm10)


if __name__ == "__main__":

    run()