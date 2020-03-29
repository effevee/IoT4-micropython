from machine import Pin, PWM, I2C, Timer
from esp8266_i2c_lcd import I2cLcd
import ssd1306
from tijd import LocalTime
import utime

# constanten
KNOPPin = [25, 26]
LEDPin = 18
lcd_i2c_address = 0x3F  # decimaal 63
oled_i2c_address = 0x3C # decimaal 60

# globale variabelen
class myGlobals:
    knop = []           # knop objecten
    knop_ids = {}       # koppelt knop objecten aan index
    knop_val = []       # knop waarde
    led = None          # led object
    now = ''            # tijd hh:mm:ss
    intensity = 512     # intensiteit lcd 0-1023
    debounce_ms = 20    # debounce tijd knoppen


# callback timer aanpassen tijd
def getTime(timer):
    # haal locale tijd op
    res = lt.getLocalTime()
    # filter tijdstring eruit en bewaar in globale variabele
    if res[0] == 0:
        lts = str(res[1])
        myGlobals.now = lts[11:]
        

# callback timer tekenen intensiteit LCD op oled
def drawIntensity(timer):
    # procent intensiteit berekenen (PWM 0-1023)
    procent = int((myGlobals.intensity*100) // 1023)
    oled.fill(0)
    oled.rect(12, 28, 100, 12, 1)
    oled.fill_rect(12, 28, procent, 12, 1)
    oled.show()
    

# callback pin drukknoppen
def setIntensity(pin):
    # welke drukknop ?
    knop = myGlobals.knop_ids[str(pin)]
    #print(knop)
    # status
    if myGlobals.knop_val[knop]:
        # True
        return
    # debounce tijd wachten
    utime.sleep_ms(myGlobals.debounce_ms)
    # update intensity
    if knop == 0:  # links = verminderen
        if myGlobals.intensity < 20:
            myGlobals.intensity = 0
        else:
            myGlobals.intensity -= 20
    else:   # rechts = vermeerderen
        if myGlobals.intensity > 1003:
            myGlobals.intensity = 1023
        else:
            myGlobals.intensity += 20
    # status terug False
    myGlobals.knop_val[knop] = False


# i2c, lcd en oled instances
i2c = I2C(scl=Pin(21), sda=Pin(22))
lcd = I2cLcd(i2c, lcd_i2c_address, 2, 16)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr = oled_i2c_address)

# knop instances
for i in range(len(KNOPPin)):
    myGlobals.knop.append(Pin(KNOPPin[i], Pin.IN, Pin.PULL_UP))
    myGlobals.knop[i].irq(trigger=Pin.IRQ_RISING, handler=setIntensity)
    myGlobals.knop_ids.update({str(myGlobals.knop[i]):i})   
    myGlobals.knop_val.append(False)
    
# led instance (PWM)
myGlobals.led = PWM(Pin(LEDPin), freq=100)
myGlobals.led.duty(myGlobals.intensity)
    
# localtime instance
lt = LocalTime(1, debug=False)

# instellen RTC op esp32
lt.startInternetTime()

# timer voor aanpassen van de tijd (iedere seconde)
timer1 = Timer(0)
timer1.init(period=1000, mode=Timer.PERIODIC, callback=getTime)

# timer voor aanpassen van de intensiteit van de LCD (iedere 250 ms)
timer2 = Timer(1)
timer2.init(period=250, mode=Timer.PERIODIC, callback=drawIntensity)



try:
    # oneindige lus
    while True:
        # toon tijd op LCD
        lcd.clear()
        lcd.move_to(4,0)
        lcd.putstr(myGlobals.now)
        # update intensiteit led
        myGlobals.led.duty((myGlobals.intensity*100) // 1023)
        # even wachten
        utime.sleep_ms(500)

except Exception as E:
    print('Fout: ', E)
    
finally:
    timer1.deinit()
    timer2.deinit()
    myGlobals.led.deinit()
    oled.poweroff()
    print('Programma onderbroken')
    
    