from lora import rak811
import binascii
import utime

class rak811P2P(rak811):

    def __init__(self,RxTx,baudrate,freq=868500000,bandwidth=125,spreading=7,codingrate=1,preamble=5,power=5,debug=False):
        self.freq = freq
        self.bandwidth = bandwidth
        self.spread = spreading
        self.coderate = codingrate
        self.preamble = preamble
        self.power = power
        super().__init__(RxTx,baudrate,debug)
    
    def start(self):
        try:
            if super().start() == "OK":
                #werkmode op P2P zetten
                utime.sleep_ms(20)
                self.serdev.write(str.encode("at+set_config=lora:work_mode:1\r\n"))
                res=self.isOK(10,"OK")
                if res == "NOK":
                    if self.debug:
                        print("change mode to P2P not OK")
                    return "NOK"
                    
                #vertalen bandbreedte van 125,250 of 500 kHz naar 0,1 of 2
                posBandWidths = {125:0,250:1,500:2}
                self.bandwidth=posBandWidths.get(self.bandwidth,0)
                #controle spreading (van 7 t.e.m. 12)                
                if not ( 7 <=  self.spread  <= 12 ):
                    self.spread = 7
                #controle codingrate
                if self.coderate < 1 or self.coderate>4:
                    self.coderate = 1
                #controle preamble
                if self.preamble < 5 or self.preamble>65535:
                    self.preamble = 5
                #controle power
                if self.power < 5 or self.power>14:
                    self.power = 5
                    
                #communicatie parameters zetten
                sendSettingStr = "lorap2p:"+str(self.freq)+":"+str(self.spread)+":"+str(self.bandwidth)+":"+str(self.coderate)+":"+str(self.preamble)+":"+str(self.power)
                self.serdev.write(str.encode("at+set_config="+sendSettingStr+"\r\n"))
                res = self.isOK(10,"OK")
                if res == "NOK" and self.debug:
                    print("problem P2P config params")
                    return ("NOK")
                return ("OK")
            else:
                if self.debug:
                    print("problem start RAK811")
                return "NOK"
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK"
    
    def send(self, msg, useChecksum = False, times=1, interval_ms=0):
        try:
            Hex=binascii.hexlify(msg.encode("utf-8"))
            
            #get the checksum if requisted
            checksum = ""
            if useChecksum :
                res = self.calcChecksum(Hex)          
                if "NOK" in res.upper():
                    checksum ="00" # a checksum of "00" means an error (see function 'calcChecksum')
                else:
                    checksum = res

            #Send the message according schedule
            for _ in range(times) :  
                if self.debug:
                        print(str(Hex.decode())+ checksum)
                self.serdev.write(str.encode("at+send=lorap2p:"+str(Hex.decode())+ checksum + "\r\n"))
                if "NOK" in self.isOK(5,"OK").upper():
                    if self.debug:
                        print("NOK TxFaulty")
                    return "NOK send"
                if _ != times :#hold for a certain time, if the loop is not at last position
                    utime.sleep_ms(interval_ms)
            return "OK send"
            
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK send"
    
    def recv(self, useChecksum = False):#ontvangen van een boodschap
        try:
            res=self.serdev.readline()
            #wordt verwacht : at+recv=a,b,c:XYZ met a,b,c getallen en XYZ de boodschap
            if res is not None:
                res=res.decode()
                if not "AT+RECV" in res.upper():#functie wordt verlaten indien geen at+recv
                    if self.debug:
                        print("geen goede boodschap ( at+recv ontbreekt)")
                    return "NOK"
                parts = res.split(':')
                if len(parts) < 2:
                    if self.debug:
                        print("geen goede boodschap ( : ontbreekt)")
                    return "NOK"                   
                res = parts[1][:-2] #nu zit XYZ\r\n in res als string en wordt CR/NL verwijderd
                res = res.encode() #nu zijn het bytes
                res=binascii.unhexlify(res).decode("utf-8")#hexbytes omzetten naar stringbytes en dan decode
                
                if useChecksum :
                    #get the received checksum
                    recvChecksum = res[-2:] #received checksum
                    if recvChecksum =="00":
                        if self.debug:
                            print("checksum is 00")
                        return "NOK recv"
                    res = res[:-2] #The clean received message (without the checksum)
                    #calc the checksum of the received message
                    calcChecksum = self.calcChecksum(binascii.hexlify(res.encode()))          
                    if not "NOK" in calcChecksum.upper():
                        return "NOK recv"                           
                    else:
                        #compare calculated and received checksum:
                        if calcChecksum != recvChecksum:
                            if self.debug:
                                print("Received message is corrupt")
                            return "NOK recv"  
                        #All IS FINE => PROCEED
                        
                return "msg=" + res
            else:
                if self.debug:
                    print("niets ontvangen")
                return "NOK" 
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK"
    
    def getConfigParams(self):
        config={"freq":self.freq,"bandwidth":self.bandwidth,"spreading":self.spread,"coderating":self.coderate,"preamble":self.preamble,"power":self.power}
        return config
    
    def getStatus(self):
        try:
            self.serdev.write(str.encode("at+get_config=lora:status\r\n"))
            #antwoord ontvangen
            return self.isOK(40,"LIST END") #peer to peer heeft een LIST END
            
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK"
    
    def calcChecksum(self,dataInHex):
        '''
        Function to calculate a checksum according the given hexbytes.
        ==============================================================
        Formula:
            Result = 98 - ( modulo 97 of the sum of all ascii values (in decimal format) from each ietm in a hexarray)
        
        Remark:    
            The checksum is valid between 1 and 98
        
        The result is stored in self.checksum as a string
        '''
        try:
            checksum = 0
            for valItem in dataInHex:
                checksum += valItem
            checksum = 98 - ( checksum%97 )
            
            if checksum < 0 or checksum > 98 :
                if self.debug:
                    print("Incorrect checksum calculation")
                return "NOK calcChecksum"
                
            #convert to a string with a fixed lenght of 2 filled with zeros
            checksum = str(checksum)
            for i in range (2-len(checksum)):
                checksum = "0"+checksum    
            
            if self.debug:
                    print("Checksum= " + checksum )
            
            return checksum
            
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK calcChecksum"