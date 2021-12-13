import airbit
import json
"""
Asserts the modem
"""
iot = airbit.setup()

payload = {"heartbeat": 1}
payload = json.dumps(payload)
iot.send(payload)
