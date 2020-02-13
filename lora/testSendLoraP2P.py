from loraModes import rak811P2P
import utime

raks = rak811P2P(1, 115200, freq=868300000, spreading=7, debug=True)
res = raks.start()
if res == "OK":
    print(raks.getStatus())
    for count in range(500):
        utime.sleep_ms(500)
        msg = "Effevee" + str(count)
        raks.send(msg)
    raks.stop()