from machine import UART
import utime

class rak811:
    
    def __init__(self,RxTxPort,baudrate,debug=False):
        
        self.RxTx = RxTxPort #RxTx koppel, normaal 1 of 2
        self.bd = baudrate
        self.debug = debug
        self.serdev = None #instance voor UART
        self.version = ""
    
    def start(self):
        try:
            self.serdev = UART(self.RxTx,self.bd)#maken van UART instance
            #Opvragen van versie
            self.serdev.write(str.encode("at+version\r\n"))
            #antwoord ontvangen
            return self.isOK(5,"OK")
            
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK"
    
    def stop(self):#stop seriële bus
        try:
            if self.serdev != None:#indien ze bestaat
                self.serdev.deinit()
                del self.serdev#verwijderen van het object (foutje was, self vergeten!)
                self.version = ""
            return "OK"
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK"
    
    def send(self):
        pass
    
    def recv(self):
        pass
    
    def getVersion(self):
        return self.version
    
    def getStatus(self):
        pass

    def calcChecksum(self):
        pass    

    def isOK(self,lines,stop):
        try:
            counter = 0
            while counter < lines:#werken met teller om meerdere lijnen te lezen
                utime.sleep_ms(20)
                res=self.serdev.readline()
                if res == None:
                    counter+=1
                    continue
                res = res.decode("utf-8")
                if self.debug:
                    print("isOK= " + str(res))
                if stop.upper() in res.upper() :#LIST END in antwoord = OK
                    return "OK"
                counter +=1
            return "NOK"#Nergens OK = NOK
        except Exception as E:
            if self.debug:
                print(E)
            return "NOK" 