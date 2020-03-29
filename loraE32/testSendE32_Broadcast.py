###########################################
# sending broadcast
# transmitter - address 0000 - channel 04
# receiver(s) - address xxxx - channel 04
###########################################

from loraE32 import ebyteE32
import utime

M0pin = 25
M1pin = 26
AUXpin = 27

e32 = ebyteE32(M0pin, M1pin, AUXpin, Address=0x0001, Channel=0x04, debug=True)

e32.start()

address = 0x0000
channel = 0x04
message = "HELLO WORLD "

teller = 0
while True:
    print('Sending broadcast : address %s - channel %d - message %s'%(address, channel, message +str(teller)))
    e32.sendMessage(address, channel, message + str(teller))
    teller += 1
    utime.sleep_ms(2000)

print(e32.config)
e32.stop()