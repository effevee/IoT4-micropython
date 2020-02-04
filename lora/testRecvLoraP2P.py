from loraModes import rak811P2P

rakr = rak811P2P(1, 115200, debug=True)

res = rakr.start()

if res == "OK":
    print(rakr.getStatus())
    
    for count in range(20):
        print(rakr.recv())
    
    rakr.stop()