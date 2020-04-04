from machine import Pin,deepsleep
import esp32
import utime

# wakeup button
wakeup = Pin(25, Pin.IN, Pin.PULL_UP)

# esp32 external wakeup
esp32.wake_on_ext0(pin=wakeup, level=esp32.WAKEUP_ALL_LOW)

# countdown
for i in range(10,0,-1):
    print('deepsleep in %d seconds'%(i))
    utime.sleep(1)
    
# deepsleep for 10 sec
print('deepsleep until button press')

# deepsleep
deepsleep()

