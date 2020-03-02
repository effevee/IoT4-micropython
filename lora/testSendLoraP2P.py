from loraModes import rak811P2P
import utime

raks = rak811P2P(1, 115200, freq=868000000, spreading=7, preamble=6, debug=True)
res = raks.start()
if res == "OK":
    print(raks.getStatus())
    for count in range(100):
        utime.sleep_ms(500)
        msg = "Effevee" + str(count)
        raks.send(msg)
    raks.stop()