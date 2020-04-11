###########################################
# sending fixed monitor
###########################################
# transmitter - address 0001 - channel 02
# message     - address 0003 - channel 04
# receiver    - address FFFF - channel 04
###########################################

from loraE32 import ebyteE32
import utime

M0pin = 25
M1pin = 26
AUXpin = 27

e32 = ebyteE32(M0pin, M1pin, AUXpin, Address=0x0001, Channel=0x02, debug=False)

e32.start()

to_address = 0x0003
to_channel = 0x04

teller = 0
while True:
    message = 'HELLO WORLD %s'%str(teller)
    print('Sending fixed monitor : address %s - channel %d - message %s'%(to_address, to_channel, message))
    e32.sendMessage(to_address, to_channel, { 'msg':message })
    teller += 1
    utime.sleep_ms(2000)

e32.stop()