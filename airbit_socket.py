class AirBitSocket():
    def __init__(self, ip, port):
        self.sock = None
        self.ip = ip
        self.port = port

    def init(self):
        if not self.sock:
            self.sock = socket.socket()
            self.sock.connect(socket.getaddrinfo(
                self.ip, self.port)[0][-1])
            return self.sock

    def send(self, time, temperature: int, humidity: int, pm25: float, pm10: float, northing: str, easting: str):
        import json
        data = {"time": time, "temperature": temperature, "humidity": humidity,
                "pm25": pm25, "pm10": pm10, "northing": northing, "easting": easting}
        body = json.dumps(data)
        content_len = len(body)
        # print(body, content_len, type(body))
        # self.sock.setblocking(True)
        # self.sock.send(
        #     b"POST /sensors/add HTTP/1.1\r\nHost: 51.107.211.213:8080\r\nConnection: Keep-Alive\r\nKeep-Alive: timeout=5, max=1000\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s" % (content_len, body))
        # self.sock.setblocking(False)
        # Mike murphys edited micropython library
        try:
            resp = urequests.request(
                "POST", "http://51.107.211.213:8080/sensors/add", json=data)
            print(resp.status_code)
        except OSError:
            pass
        # print(self.sock.recv(4096))

    def heartbeat(self):
        """
        Check connection of server
        """
        self.sock.send(b"GET / HTTP/1.1\r\n\r\n")
        response = self.sock.recv(4096)
        print(response)

    def close(self):
        self.sock.close()
