from loraE32 import ebyteE32

M0pin = 25
M1pin = 26
AUXpin = 27

e32 = ebyteE32(M0pin, M1pin, AUXpin, '868T20D', 'U1', 9600, '8N1', '2.4k', 0x0000, 0x06, debug=True)

e32.start()
e32.getConfig()
e32.getVersion()

e32.stop()