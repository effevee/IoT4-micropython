from loraModes import rak811P2P
import utime

raks = rak811P2P(1, 115200, freq=868300000, debug=True)
res = raks.start()
if res == "OK":
    print(raks.getStatus())
    for count in range(100):
        utime.sleep_ms(100)
        msg = "Effevee" + str(count)
        raks.send(msg)
    raks.stop()