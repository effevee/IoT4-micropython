import serial
import time
import binascii

def readLora(ser):
    res=ser.readline()
    if res != None:
        print(res)
        res = res.decode()
        parts = res.split(":")
        if len(parts)>1:
            d=parts[1][0:-2].encode()
            bStr=binascii.unhexlify(d)
            print(bStr.decode())
            return bStr.decode()
    else:
        return "NOK"

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
try:
    while True:
        msg = "test:"+str(count)
        Hex=binascii.hexlify(msg.encode())
        sendMsg = "at+send=lorap2p:"+str(Hex.decode())+"\r\n"
        ser.write(sendMsg.encode())
        res=readLora(ser)
        if res != None:
            if "#next" in res:
                parts=res.split(":")
                if parts[1][:-5] == str(count):
                    count+=1
        time.sleep(1)

except Exception as E:
    print(E)
finally:
    ser.close()
