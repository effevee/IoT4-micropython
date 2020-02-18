import serial
import time
import binascii

port = "/dev/serial0" #seriêle poort
baud=115200 #zendsnelheid
ser=serial.Serial(port,baud,timeout=1)#Maken instance van klasse Serial
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

ser.close()
