from machine import Pin, I2C
from esp8266_i2c_lcd import I2cLcd

# adress i2c module LCD
i2c_address = 0x3F  # decimaal 63

# i2c en lcd instances
i2c = I2C(scl=Pin(21), sda=Pin(22))
lcd = I2cLcd(i2c, i2c_address, 2, 16)

# zet iets op lcd
lcd.putstr('Hallo daar!')
          