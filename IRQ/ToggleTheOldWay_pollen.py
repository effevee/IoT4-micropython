from machine import Pin
import utime

# GPIO pins 
LED = 18
KNOP = 21

# led en knop instances
led = Pin(LED, Pin.OUT)
knop = Pin(KNOP, Pin.IN, Pin.PULL_UP)

try:
    # oneindige lus
    while True:
        # knop ingedukt
        if knop.value() == 0:
            # wachten tot knop losgelaten wordt
            while knop.value() == 0:
                utime.sleep_ms(20)
            # led togglen
            led.value(not led.value())
    
except:
    print('Programma onderbroken')
    
finally:
    led.value(0)
