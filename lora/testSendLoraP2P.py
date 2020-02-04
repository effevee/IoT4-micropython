from loraModes import rak811P2P
import utime

raks = rak811P2P(1, 115200, debug=True)

res = raks.start()

if res == "OK":
    print(raks.getStatus())
    
    for count in range(20):
        utime.sleep_ms(20)
        msg = "Frank" + str(count)
        raks.send(msg)
    
    raks.stop()