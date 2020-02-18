import serial
import time
import binascii
import random

port = "/dev/serial0" #seriêle poort
baud=115200 #zendsnelheid
ser=serial.Serial(port,baud,timeout=0.5)#Maken instance van klasse Serial
time.sleep(2) #rust na connectie, tijd nodig om te connecteren.
#print(ser.readline())
ser.write(str.encode("at+version\r\n"))
print(ser.readline())

ser.write(str.encode("at+get_config=lora:status\r\n"))
cnt=0
while cnt<50:
    res = ser.readline()
    res = res.decode("utf-8")
    time.sleep(0.02)
    if "List End" in res:
        break
    print(res)
    cnt+=1

ser.write(str.encode("at+set_config=lora:work_mode:1\r\n"))
cnt=0
while cnt <10:
    res = ser.readline()
    res = res.decode("utf-8")
    print(res)
    if "OK" in res:
        print("LORA mode P2P")
        break
    cnt+=1

time.sleep(1)
ser.write(str.encode("at+set_config=lorap2p:868000000:7:0:1:6:9\r\n"))
while cnt<50:
    res = ser.readline()
    res = res.decode("utf-8")
    time.sleep(0.02)
    if "OK" in res or res == "" or res =="\r\n":
        break
    print(res)
    print(cnt)
    cnt+=1

ser.write(str.encode("at+get_config=lora:status\r\n"))
cnt=0
while cnt<40:
    res = ser.readline()
    if res == None:
        break
    res = res.decode("utf-8")
    if "at+recv" in res or "List End" in res:
        break
    time.sleep(0.02)
    print(res)
    cnt+=1

num = 0
try:
    while True:
        temp = random.randint(0,45)
        hum = random.randint(0,100)
        for t in range(20):
            msg = "{\"id\":\"000\",\"DHT11_temperature\":\""+str(temp)+"\",\"DHT11_humidity\":\""+str(hum)+"\",\"datasetId\":\""+str(num)+"\"}"
            print(msg)
            Hex=binascii.hexlify(msg.encode())
            sendMsg = "at+send=lorap2p:"+str(Hex.decode())+"\r\n"
            ser.write(sendMsg.encode())
            time.sleep(0.5)
        time.sleep(50)
        num+=1

except Exception as E:
    print(E)
finally:
    ser.close()
