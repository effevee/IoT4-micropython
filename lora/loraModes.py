from lora import rak811
import ubinascii
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
                res = self.isOK(10, "OK")
                if res == "NOK":
                    if self.debug:
                        print("change mode to P2P not OK")
                    return "NOK"
                
                # translate bandwidth 125, 250, 500 kHz to 0, 1, 2
                posBandWidths = {125:0, 250:1, 500:2}
                self.bandwidth=posBandWidths.get(self.bandwidth, 0)
                # control spreading
                if self.spread < 6 or self.spread > 12:
                    self.spread = 6
                # control codingrate
                if self.coderate < 1 or self.coderate > 4:
                    self.coderate = 1
                # control preamble
                if self.preamble < 5 or self.preamble > 65535:
                    self.preamble = 5
                # control power
                if self.power < 5 or self.power > 14:
                    self.power = 5
                
                # set communication parameters
                sendSettingStr = "lorap2p:" + str(self.freq) + ":" + str(self.spread) + ":" + str(self.bandwidth) + ":" + str(self.coderate) + ":" + str(self.preamble) + ":" + str(self.power)
                self.serdev.write(str.encode("at+set_config=" + sendSettingStr + "\r\n"))
                res = self.isOK(10, "OK")
                if res == "NOK" and self.debug:
                    print("problem with P2P config params")
                    return "NOK"
                return "OK"
            else:
                if self.debug:
                    print("problem with start RAK811")
                return "NOK"
        
        except Exception as E:
            if self.debug:
                print("Error on start P2P: ",E)
            return "NOK"

    
    def send(self,msg):
        try:
            Hex = ubinascii.hexlify(msg.encode("utf-8"))
            if self.debug:
                print(Hex)
            self.serdev.write(str.encode("at+send=lorap2p:" + str(Hex.decode()) + "\r\n"))
            res = self.isOK(5, "OK")
            return res
        
        except Exception as E:
            if self.debug:
                print("Error on send P2P: ", E)
            return "NOK"

    
    def recv(self):
        try:
            res = self.serdev.readline()
            if res == None:
                if self.debug:
                    print('No response')
                return "NOK"
            else:
                res = res.decode('utf-8')
                if self.debug:
                    print(res)
                if "at+recv" in res:
                    # at+recv=a,b,c:XYZ\r\n
                    # with a,b,c receive status info and XYZ the payload message
                    msg = res.split(":")
                    if len(msg) < 2:
                        if self.debug:
                            print('No valid message payload')
                        return "NOK"
                    # remove \r\n from the end of the payload
                    msg = msg[1][:-2]  
                    msg = ubinascii.unhexlify(msg).decode('utf-8')
                    return 'msg=' + msg
                else:
                    print('No at+recv response')
                    return "NOK"
                            
        except Exception as E:
            if self.debug:
                print("Error on receive P2P: ", E)
            return "NOK"
        
        
    def getConfigParams(self):
        config = {"freq":self.freq, "bandwidth":self.bandwidth, "spreading":self.spread, "coderating":self.coderate, "preamble":self.preamble, "power":self.power}
        return config


    def getStatus(self):
        try:
            self.serdev.write(str.encode("at+get_config=lora:status\r\n"))
            return self.isOK(30, "List End")
        
        except Exception as E:
            if self.debug:
                print('Error on getStatus: ',E)
            return "NOK"
