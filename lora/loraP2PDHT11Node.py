import json
import simpleWifi
from umqtt.robust import MQTTClient
import sys
import utime
from tempSensors import tempDHT11
from humSensors import humDHT11
from loraModes import rak811P2P
from machine import deepsleep
from machine import ADC
from machine import Pin

BROKER="192.168.10.180" #IP Broker
sSettings=""
factor=0.6


class Topics:
    nodeId="000"
    topicSettings="lorap2p/settings"+nodeId
    topicResponse="lorap2p/response"+nodeId
    response=False

#callback voor MQTT
def mqttMsg(topic,msg):
    msg=msg.decode("utf-8")
    print(msg)
    #plaatsen van response node-red in json bestand
    fJson = None
    try:
        fJson=open("settingsLoraP2P.json","w");
        fJson.write(msg+"\n")
    except Exception as E:
        print(E)
        print("problem to create new json file")
    finally:
        if fJson is not None:
            fJson.close()
            Topics.response = True

#Ophalen zendparameters (zitten in een json bestand)
fJson = None
try:
    fJson=open("settingsLoraP2P.json","r");
    for l in fJson:
        sSettings+=l
except Exception as E:
    print(E)
    print("problem reading json file")
    sSettings="{}"
finally:
    if fJson is not None:
        fJson.close()

led_board=Pin(2,Pin.OUT)
#Verbinden met Wifi om de node via mqtt en node-red opnieuw te kunnen instellen
myWifi = None
mqttCl = None
myWifi = simpleWifi.Wifi()

if not(myWifi.open()):
    myWifi.get_status()
    print("no connection with Wifi .....")
    if sSettings=="{}":#indien geen verbinding met Wifi en nog geen zend parameters, verlaat het programma
        print("no sendparameters on the node ...")
        sys.exit()
myWifi.get_status()
print(myWifi.get_IPdata())

try:
    if not (myWifi.get_IPdata() == "" or myWifi.get_IPdata()[0]=="0.0.0.0"):
        mqttCl=MQTTClient("espLoraP2P"+Topics.nodeId,BROKER)
        mqttCl.set_callback(mqttMsg)
        mqttCl.connect()
        mqttCl.publish(Topics.topicSettings,sSettings)
        mqttCl.subscribe(Topics.topicResponse)
        delay = 40000 #Indien verbinding met Wifi en settings zijn ingevuld, wacht 40s anders wacht 90s
        if sSettings == "{}":
            delay=90000
        #maximaal 1.5 minuten wachten op respons node-red, onboard LED brand om duidelijk te maken dat er wijzigingen mogelijk zijn via node-red
        led_board.value(1)
        stopTime = utime.ticks_add(utime.ticks_ms(), delay)
        while utime.ticks_diff(stopTime, utime.ticks_ms()) > 0 and not Topics.response:
            mqttCl.check_msg()
    if Topics.response == False and sSettings=="{}":
        print("No response from node-red and no settings, exit program!")
        led_board.value(0)
        sys.exit()
    Topics.response = False
    led_board.value(0)
    
except Exception as E:
    print(E)
    print("problems with Wifi or MQTT")
finally:
    if mqttCl is not None:
        del mqttCl
    if myWifi is not None:
        myWifi.close()
        del myWifi
    led_board.value(0)

#Ophalen lora parameters, verbinden lora P2P netwerk, meten en deepsleep

#openen van json bestand om zend parameters op te halen
fJson = None
js=None
try:
    #Pin om spanning batterij te meten
    adcPin = ADC(Pin(36))
    adcPin.atten(adcPin.ATTN_11DB)

    fJson=open("settingsLoraP2P.json","r");
    js=json.load(fJson)
    if js is None:
        print("problem to parse JSON")
        sys.exit()
except Exception as E:
    print(E)
    print("problem reading json file")
    sys.exit()
finally:
    if fJson is not None:
        fJson.close()
    
print(js)
try:
    #init rak
    temp1=None
    hum1=None
    rak811 = rak811P2P(2,115200,freq=int(js["freq"]),bandwidth=int(js["bdw"]),spreading=int(js["spread"]),codingrate=int(js["bitrate"]),preamble=int(js["preamble"]),power=int(js["power"]),debug=True)
    res = rak811.start()
    if res == "NOK":
        print("problem init RAK811, quit the application")
        sys.exit()
    print(rak811.getStatus())
    
    #init sensoren
    sens = []
    stats = []
    hum1 = humDHT11(23,"DHT11 humidity",debug=True)
    sens.append(hum1)
    temp1 = tempDHT11(23,"DHT11 temperature",debug=True)
    sens.append(temp1)
    for s in sens:
        res=s.start()
        if res[0]<0:
            print("problem starting sensor")
            sys.exit()
    
    #meten
    msg="{\"id\":\""+Topics.nodeId+"\",data0,data1,bat,\"datasetId\":\""+str(js["datasetId"])+"\"}"
    i=0
    for s in sens:
        res=s.meet()
        info=s.getInfo().replace(" ","_")
        msg=msg.replace("data"+str(i),"\""+info+"\":\""+str(res[1])+"\"")
        i+=1
    vBat=(adcPin.read()/1024)*3.3*factor
    msg=msg.replace("bat","\"bat\":\""+str(vBat)+"\"")
    print(msg)
    
    #verzenden van boodschap via lora (een burst van 20 dezelfde boodschappen om de 200ms één).
    for cnt in range(20):
        print(rak811.send(msg))
        led_board.value(1)
        utime.sleep_ms(200)
        led_board.value(0)
    
    #Dataset Id met 1 verhogen, als dataset Id > 1000 dan terug 0 en vervolgens schrijven naar json bestand
    n=int(js["datasetId"])
    n+=1
    if n>1000:
        n=0
    js["datasetId"]=str(n)
    
    fJson = open("settingsLoraP2P.json", "w")
    fJson.write(json.dumps(js))
    fJson.close()
    
    #Ga in deepsleep mode voor (hier nu) 1/2 minuut
    print("****deepsleep********")
    deepsleep(1800000)
    print("****leave deepsleep********")
    
except Exception as E:
    print("problems measure or lora procedure")
    print(E)
finally:
    if temp1 is not None:
        temp1.stop()
    if hum1 is not None:
        hum1.stop()
    rak811.stop()
    



        
        
    
    
    
            
    
    
    
    
    
    
    
    
    
        





        
    