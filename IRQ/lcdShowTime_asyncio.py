from machine import Pin, I2C, Timer
from esp8266_i2c_lcd import I2cLcd
from tijd import LocalTime
import uasyncio as asyncio
import utime

class myGlobals:
    now = ''
    

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
        await asyncio.sleep(1)
    

# adress i2c module LCD
i2c_address = 0x3F  # decimaal 63

# i2c en lcd instances
i2c = I2C(scl=Pin(21), sda=Pin(22))
lcd = I2cLcd(i2c, i2c_address, 2, 16)

# localtime instance
lt = LocalTime(1, debug=False)

# instellen RTC op esp32
lt.startInternetTime()


try:
    # event loop scheduler initialiseren
    loop = asyncio.get_event_loop()
    # taken op de event loop queue zetten
    loop.create_task(getTime())
    # taken laten uitvoeren
    loop.run_forever()

except Exception as E:
    print('Fout: ', E)
    
finally:
    timer1.deinit()
    print('Programma onderbroken')
    
    