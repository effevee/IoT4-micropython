from loraModes import rak811P2P
import simpleWifi
from umqtt.robust import MQTTClient
import utime
import ujson
import sys

BROKER = "172.24.0.100"

# connect to Wifi
myWifi = None
myWifi = simpleWifi.Wifi()
if myWifi.open():
    print("Connected to Wifi")
    print(myWifi.get_IPdata())
    myWifi.get_status()
else:
    print("Problem with Wifi connection")
    sys.exit()

# connect to MQTT
mqtt_cl = None
try:
    mqtt_cl = MQTTClient('esp_frank_16', BROKER)
    mqtt_cl.connect()
        
except Exception as e:
    print('Problem connecting to MQTT broker - %s'%e)
    if myWifi is not None:
        myWifi.close()
    sys.exit()

# init RAK811
try:
    rakp2p = rak811P2P(1, 115200, freq=868000000, preamble=6, debug=False)
    res = rakp2p.start()
    if res != "OK":
        print('Problem with startup RAK')
        if myWifi is not None:
            myWifi.close()
        if mqtt_cl is not None:
            del mqtt_cl
        sys.exit()    

except Exception as e:
    print('Problem connecting to RAK811 - %s'%e)
    if myWifi is not None:
        myWifi.close()
    if mqtt_cl is not None:
        del mqtt_cl
    sys.exit()
        
print(rakp2p.getStatus())
prevId = ""
prevDataId = ""

# loop gateway
while True:
    try:
        msg = rakp2p.recv()
        utime.sleep_ms(20)
        # delete prefix msg=
        msg = msg[4:]  
        # convert json string to object
        js = ujson.loads(msg)
        if js["id"] != prevId and js["datasetId"] != prevDataId:
            mqtt_cl.publish(js["id"] + "/temp", js["DHT11_temperature"])
            mqtt_cl.publish(js["id"] + "/hum", js["DHT11_humidity"])
            prevId = js["id"]
            prevDataId = js["prevDataId"]

    except Exception as E:
        print(msg)
        print("Problem with message - %s"%E)
        continue  # back to while
        
    finally:
        rakp2p.stop()
        if myWifi is not None:
            myWifi.close()
        if mqtt_cl is not None:
            del mqtt_cl

