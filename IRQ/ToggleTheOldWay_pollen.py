from machine import Pin

LED = 18
KNOP = 21

led = Pin(LED, Pin.OUT)
knop = Pin(KNOP, Pin.IN, Pin.PULL_UP)
