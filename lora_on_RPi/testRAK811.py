import serial
import time
import binascii

port = "/dev/serial0" #seriêle poort
baud=115200 #zendsnelheid
ser=serial.Serial(port,baud,timeout=)#Maken instance van klasse Serial
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
ser.write(str.encode("at+set_config=lorap2p:869525000:7:0:1:5:5\r\n"))
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

count = 0
while count < 20:
    res=ser.readline()
    if res != None:
        print(res)
        res = res.decode()
        parts = res.split(":")
        if len(parts)>1:
            d=parts[1][0:-2].encode()
            bStr=binascii.unhexlify(d)
            print(bStr.decode())
    else:
        count+=1
    count+=1
    time.sleep(1)
    


ser.close()
