from machine import deepsleep
import utime

# countdown
for i in range(10,0,-1):
    print('deepsleep in %d seconds'%(i))
    utime.sleep(1)
    
# deepsleep for 10 sec
print('deepsleep for 10 seconds')

deepsleep(10000)

