###########################################
# receiving point to point
# transmitter - address 0001 - channel 04
# receiver    - address 0003 - channel 04
###########################################

from loraE32 import ebyteE32
import utime

M0pin = 25
M1pin = 26
AUXpin = 27

e32 = ebyteE32(M0pin, M1pin, AUXpin, Address=0x0003, Channel=0x04, debug=False)

e32.start()

address = 0x0001
channel = 0x04

while True:
    print('Receiving: address %d - channel %d'%(address, channel))
    message = e32.recvMessage(address, channel)
    utime.sleep_ms(2000)

e32.stop()