from loraE32 import ebyteE32

ee32 = ebyteE32('868T20D', 'U1', 9600, '8N1', '2.4k', 0x0000, 0x06, debug=True)

res = ee32.start()
print(res)

ee32.stop()