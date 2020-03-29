from loraE32 import ebyteE32

M0pin = 25
M1pin = 26
AUXpin = 27

e32 = ebyteE32(M0pin, M1pin, AUXpin, Address=0x0001, Channel=0x04, debug=True)

e32.start()
#e32.getConfig()
#e32.getVersion()

e32.stop()