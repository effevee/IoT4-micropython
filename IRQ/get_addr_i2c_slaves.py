from machine import Pin, I2C

i2c = I2C(scl=Pin(21), sda=Pin(22))
print(i2c.scan())
