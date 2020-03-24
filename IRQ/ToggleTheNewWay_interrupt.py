from machine import Pin
import utime

# GPIO pins 
LED = 17
KNOP = 21

class myGlobals:
    LEDState = False
    KNOPState = False
    debounce_tijd_ms = 20
    
# interrupt routine
def eventKnop(pin):
    # status?
    if myGlobals.KNOPState:
        # True
        return
    # status updaten    
    myGlobals.KNOPState = not pin.value()
    # debounce tijd wachten
    utime.sleep_ms(myGlobals.debounce_tijd_ms)
    # update LEDState
    myGlobals.LEDState = not myGlobals.LEDState
    # status terug False
    myGlobals.KNOPState = False
   

# led en knop instances
led = Pin(LED, Pin.OUT)
knop = Pin(KNOP, Pin.IN, Pin.PULL_UP)

# interrupt instellen voor knop 
knop.irq(trigger=Pin.IRQ_RISING, handler=eventKnop)

try:
    # oneindige lus
    while True:
        # led updaten    
        led.value(int(myGlobals.LEDState))
    
except:
    print('Programma onderbroken')
    
finally:
    led.value(0)
