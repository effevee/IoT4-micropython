from loraModes import rak811P2P
import utime

rakp2p= rak811P2P(2,115200,freq=867500000,spreading=7,debug=True) #maken instantie van rak811P2P
res = rakp2p.start() #start van de instantie rakp2p
if res == "OK": 
    print(rakp2p.getStatus())#status ophalen van de rak811 module
    #vorm van een boodschap : eerste letter voornaam eerste letter achternaam:test + tel.
    for i in range(3):
        msg="PD:test " +str(i)
        rakp2p.send(msg, useChecksum=True, times=5 , interval_ms=100 )#boodschap versturen

print(rakp2p.stop())#stoppen van de rak811