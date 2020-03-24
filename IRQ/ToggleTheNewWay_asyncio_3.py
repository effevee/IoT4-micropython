from machine import Pin
import uasyncio as asyncio


class myGlobals:
    LED = [17, 16, 4]       # GPIO LEDS
    LEDState = [0, 0, 0]    # LED statussen
    BUILDIN = 2             # GPIO interne LED
    KNOP = [21, 19, 18]     # GPIO drukknoppen
    debounce_time = 10      # ms

    
async def toggle_LED(nummer):
    from machine import Pin
    # instances voor led en drukknop
    led = Pin(myGlobals.LED[nummer], Pin.OUT)
    knop = Pin(myGlobals.KNOP[nummer], Pin.IN, Pin.PULL_UP)
    # led initialsatie
    led.value(myGlobals.LEDState[nummer])
    # oneindige lus
    while True:
        # knop gedrukt ?
        if knop.value() == 0:
            # debounce
            while knop.value() == 0:
                asyncio.sleep_ms(myGlobals.debounce_time)
            # toggle LED
            myGlobals.LEDState[nummer] = not myGlobals.LEDState[nummer]
        # update LED
        led.value(myGlobals.LEDState[nummer])
        # even wachten
        await asyncio.sleep_ms(myGlobals.debounce_time)
                

async def flash_buildin_led(interval):
    from machine import Pin
    buildin_led = Pin(myGlobals.BUILDIN, Pin.OUT, value=0)
    while True:
        if buildin_led.value():
            buildin_led.off()
        else:
            buildin_led.on()
        await asyncio.sleep_ms(interval)


try:
    # event loop scheduler initialiseren
    loop = asyncio.get_event_loop()
    # taken op de event loop queue zetten
    loop.create_task(flash_buildin_led(500))
    for i in range(len(myGlobals.LED)):
        loop.create_task(toggle_LED(i))
    # taken laten uitvoeren
    loop.run_forever()

except Exception as e:
    print('Probleem met asyncio - %s'%e)

finally:
    # event loop scheduler afsluiten
    loop.close()
