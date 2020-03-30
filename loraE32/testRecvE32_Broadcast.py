###########################################
# receiving broadcast (address 0xFFFF)
# transmitter - address 0001 - channel 04
# receiver(s) - address xxxx - channel 04
###########################################

from loraE32 import ebyteE32
import utime

M0pin = 25
M1pin = 26
AUXpin = 27

e32 = ebyteE32(M0pin, M1pin, AUXpin, Address=0x0003, Channel=0x04, debug=False)

e32.start()

from_address = 0xFFFF
from_channel = 0x04

while True:
    print('Receiving broadcast : address %d - channel %d'%(from_address, from_channel), end='')
    message = e32.recvMessage(from_address, from_channel)
    print(' - message %s'%(message))
    utime.sleep_ms(2000)

e32.stop()