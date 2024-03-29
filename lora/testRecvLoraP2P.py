from loraModes import rak811P2P
import utime

rakr = rak811P2P(1, 115200, freq=868000000, preamble=6, debug=False)
res = rakr.start()
if res == "OK":
    print(rakr.getStatus())
    for count in range(900):
        utime.sleep_ms(100)
        print(rakr.recv())
    rakr.stop()