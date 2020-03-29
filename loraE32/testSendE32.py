from loraE32 import ebyteE32
import utime

M0pin = 25
M1pin = 26
AUXpin = 27

e32 = ebyteE32(M0pin, M1pin, AUXpin, '868T20D', 'U1', 9600, '8N1', '2.4k', 0x0000, 0x06, debug=True)

e32.start()

address = 0x0000
channel = 0x06
#message = "HELLO WORLD "

teller = 0
while True:
    print('Sending: address %d - channel %d - message %d'%(address, channel, teller))
    e32.sendMessage(address, channel, teller)
    teller += 1
    utime.sleep_ms(2000)

e32.stop()