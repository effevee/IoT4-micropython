from loraModes import rak811P2P
import utime

rakp2p= rak811P2P(2,115200,debug=True,freq=868100000) #maken instantie van rak811P2P
res = rakp2p.start() #start van de instantie rakp2p
if res == "OK": 
    print(rakp2p.getStatus())#status ophalen van de rak811 module

    #vorm van een boodschap : eerste letter voornaam eerste letter achternaam:test + tel.
    for i in range(20):
        print(rakp2p.recv(useChecksum=True))
        utime.sleep_ms(200)

print(rakp2p.stop())#stoppen van de rak811