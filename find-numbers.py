from network import LTE
# prints out IMEI numbers to use for coap connectiont
lte = LTE()
lte.send_at_cmd("AT+CIMI")
lte.send_at_cmd("AT+CGSN")
