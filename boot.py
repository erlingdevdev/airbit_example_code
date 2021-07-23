# from network import WLAN
# import machine

# wlan = WLAN(mode=WLAN.STA)

# wlan.ifconfig(config=("192.168.1.107", "255.255.255.0",
#               "192.168.1.1", "192.168.1.1"))

# nets = wlan.scan()
# for net in nets:
#     if net.ssid == 'odslab':
#         print('Network found!')
#         wlan.connect(net.ssid, auth=(net.sec, 'torsdag2021'), timeout=5000)
#         while not wlan.isconnected():
#             machine.idle()  # save power while waiting
#         print('WLAN connection succeeded!')
#         break
