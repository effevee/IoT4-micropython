from machine import Pin, PWM, I2C, Timer
from esp8266_i2c_lcd import I2cLcd
import ssd1306
from tijd import LocalTime
import uasyncio as asyncio
from uasyncio.synchro import Lock
import utime

# constanten
KNOPPin = [25, 26]
LEDPin = 18
lcd_i2c_address = 0x3F  # decimaal 63
oled_i2c_address = 0x3C # decimaal 60

# globale variabelen
class myGlobals:
    knop = []           # knop objecten
    mult = []           # knop mult (1=vermeerderen -1=verminderen)
    led = None          # led object
    now = ''            # tijd hh:mm:ss
    intensity = 512     # intensiteit lcd 0-1023
    debounce_ms = 10    # debounce tijd knoppen


# coroutine ophalen tijd
async def getTime():
    # oneindige lus
    while True:
        # haal locale tijd op
        res = lt.getLocalTime()
        # filter tijdstring eruit en bewaar in globale variabele
        if res[0] == 0:
            lts = str(res[1])
            myGlobals.now = lts[11:]
        # LCD scherm leegmaken
        lcd.clear()
        # toon de tijd op LCD scherm
        lcd.move_to(4,0)
        lcd.putstr(myGlobals.now)
        # coroutine 1 sec pauzeren
        await asyncio.sleep_ms(1000)
        

# coroutine tekenen intensiteit LCD op oled
async def drawIntensity():
    # oneindige lus
    while True:
        # procent intensiteit berekenen (PWM 0-1023)
        procent = int((myGlobals.intensity*100) // 1023)
        oled.fill(0)
        oled.rect(12, 28, 100, 12, 1)
        oled.fill_rect(12, 28, procent, 12, 1)
        oled.show()
        # coroutine 250 ms pauzeren
        await asyncio.sleep_ms(250)
    

# coroutine intensiteit aanpassen via drukknoppen
async def setIntensity(pin, mult, lock):
    # oneindige lus
    while True:
        # knop ingedrukt
        if not pin.value():
            # debounce
            while not pin.value():
                asyncio.sleep_ms(myGlobals.debounce_ms)
            # lock om te verhinderen dat andere routines deze globale variabele kunnen aanpassen
            await lock.acquire()
            # intensiteit bijwerken
            myGlobals.intensity += 50*mult
            if myGlobals.intensity < 0:
                myGlobals.intensity = 0
            if myGlobals.intensity > 1023:
                myGlobals.intensity = 1023
            # lock vrijgeven
            await asyncio.sleep_ms(myGlobals.debounce_ms)
            lock.release()
        # coroutine pauzeren
        await asyncio.sleep_ms(50)


# coroutine LED intensiteit aanpassen
async def LEDIntensity():
    # oneindige lus
    while True:
        # LED intenteit aanpassen
        myGlobals.led.duty(myGlobals.intensity)
        # coroutine pauzeren
        await asyncio.sleep_ms(50)
        

# i2c, lcd en oled instances
i2c = I2C(scl=Pin(21), sda=Pin(22))
lcd = I2cLcd(i2c, lcd_i2c_address, 2, 16)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr = oled_i2c_address)

# knop instances
for i in range(len(KNOPPin)):
    myGlobals.knop.append(Pin(KNOPPin[i], Pin.IN, Pin.PULL_UP))
    if i == 0:
        myGlobals.mult.append(-1)
    else:
        myGlobals.mult.append(1)
    
# led instance (PWM)
myGlobals.led = PWM(Pin(LEDPin), freq=100)
myGlobals.led.duty(myGlobals.intensity)
    
# localtime instance
lt = LocalTime(1, debug=False)

# instellen RTC op esp32
lt.startInternetTime()

try:
    # event loop scheduler initialiseren
    loop = asyncio.get_event_loop()
    # taken op de event loop queue zetten
    loop.create_task(getTime())
    loop.create_task(drawIntensity())
    lock = Lock()
    for i in range(len(KNOPPin)):
        loop.create_task(setIntensity(myGlobals.knop[i], myGlobals.mult[i], lock))
    loop.create_task(LEDIntensity())               
    # taken laten uitvoeren
    loop.run_forever()
    
except Exception as E:
    print('Fout: ', E)
    
finally:
    myGlobals.led.deinit()
    oled.poweroff()
    print('Programma onderbroken')
    
    