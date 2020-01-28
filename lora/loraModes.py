from lora import rak811
import binascii
import utime

class rak811P2P(rak811):
    ''' class for P2P communication between RAB811 LoRa modules '''
    
    def __init__(self, RxTx, baudrate, freq=869525000, bandwidth=125, spreading=7, codingrate=1, preamble=5, power=5, debug=False):
        self.freq = freq
        self.bandwidth = bandwidth
        self.spread = spreading
        self.coderate = codingrate
        self.preamble = preamble
        self.power = power
        super().__init__(RxTx, baudrate, debug)
    
    
    def start(self):
        try:
            if super().start() == "OK":
                # set P2P mode
                utime.sleep_ms(20)
                self.serdev.write(str.encode("at+set_config=lora:work_mode:1\r\n"))
                res = self.isOK(10,True)
                if res == "NOK":
                    if self.debug:
                        print("change mode to P2P not OK")
                    return "NOK"
                
                # translate bandwidth 125, 250, 500 kHz to 0, 1, 2
                posBandWidths = {125:0, 250:1, 500:2}
                self.bandwidth=posBandWidths.get(self.bandwidth,0)
                # control spreading
                if self.spread < 6 or self.spread > 12:
                    self.spread = 6
                # control codingrate
                if self.coderate < 1 or self.coderate>4:
                    self.coderate = 1
                # control preamble
                if self.preamble < 5 or self.preamble>65535:
                    self.preamble = 5
                # control power
                if self.power < 5 or self.power>20:
                    self.power = 5
                
                # set communication parameters
                sendSettingStr = "lorap2p:" + str(self.freq) + ":" + str(self.spread) + ":" + str(self.bandwidth) + ":" + str(self.coderate) + ":" +s tr(self.preamble) + ":" + str(self.power)
                self.serdev.write(str.encode("at+set_config=" + sendSettingStr + "\r\n"))
                res = self.isOK(10,True)
                if res == "NOK" and self.debug:
                    print("problem with P2P config params")
                return ("NOK")
            else:
                if self.debug:
                    print("problem with start RAK811")
                return "NOK"
        
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK"

    
    def send(self,msg):
        try:
            Hex=binascii.hexlify(msg.encode("utf-8"))
            if self.debug:
                print(Hex)
            self.serdev.write(str.encode("at+send=lorap2p:" + str(Hex.decode()) + "\r\n"))
            res = self.isOK(5,True)
            return res
        
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK"

    
    def getConfigParams(self):
        config = {"freq":self.freq, "bandwidth":self.bandwidth, "spreading":self.spread, "coderating":self.coderate, "preamble":self.preamble, "power":self.power}
        return config
