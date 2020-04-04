from machine import deepsleep
import simpleWifi
import utime

# setup wifi connection
utime.sleep(1)
myWifi = simpleWifi.Wifi()
if myWifi.open():
    print("Verbonden")
    # toon IP adres
    print(myWifi.get_IPdata())
else:
    print("Probleem met wifi")


# countdown
for i in range(10,0,-1):
    print('deepsleep in %d seconds'%(i))
    utime.sleep(1)
    
# deepsleep for 10 sec
print('deepsleep for 10 seconds')

deepsleep(10000)

