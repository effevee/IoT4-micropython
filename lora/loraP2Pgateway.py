from loraModes import rak811P2P
import simpleWifi
from umqtt.robust import MQTTClient
import utime
import ujson
import sys

# MQTT broker IP
BROKER = "192.168.1.22"
#BROKER = "172.24.0.100"
DEBUG = True

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

# init MQTT
mqtt_cl = None
try:
    mqtt_cl = MQTTClient("esp_frank_16", BROKER)
    mqtt_cl.connect()
        
except Exception as E:
    print("Problem connecting to MQTT broker - %s"%E)
    if myWifi is not None:
        myWifi.close()
    sys.exit()

# init RAK811
try:
    rakp2p = rak811P2P(1, 115200, freq=868000000, preamble=6, debug=False)
    res = rakp2p.start()
    if res != "OK":
        print("Problem with startup RAK811")
        if myWifi is not None:
            myWifi.close()
        if mqtt_cl is not None:
            del mqtt_cl
        sys.exit()    

except Exception as E:
    print("Problem connecting to RAK811 - %s"%E)
    if myWifi is not None:
        myWifi.close()
    if mqtt_cl is not None:
        del mqtt_cl
    sys.exit()
        
# status RAK811
print(rakp2p.getStatus())
# up to 6 LoRa P2P nodes can be received with ids: 000, 001, 002, 003, 004, 005
prev={"000":"","001":"","002":"","003":"","004":"","005":""}

try:
    # loop gateway
    while True:
        try:
            # receive messages
            msg = rakp2p.recv()
            utime.sleep_ms(80)
            # message not OK
            if msg == "NOK":
                continue
            # delete message prefix (msg=)
            msg = msg[4:]
            if DEBUG:
                print(msg)
            # convert json string to object
            js = ujson.loads(msg)
            # example message :
            # {"id":"000","DHT11_humidity":"46.8","DHT11_temperature":"23.0","bat":"5.661562","datasetId":"254"}
            # one of the 6 nodes contains new data
            if ["datasetId"] != prev[js["id"]]:
                mqtt_cl.publish(js["id"] + "/temp", js["DHT11_temperature"])
                utime.sleep_ms(50)
                mqtt_cl.publish(js["id"] + "/hum", js["DHT11_humidity"])
                utime.sleep_ms(50)
                # save datasetId in dictionary
                prev[js["id"]] =js["datasetId"]
                if DEBUG:
                    print(prev)

        except Exception as E:
            print("Problem with message - %s"%E)
            if DEBUG:
                print(msg)
        
finally:
    rakp2p.stop()
    if myWifi is not None:
        myWifi.close()
    if mqtt_cl is not None:
        del mqtt_cl

