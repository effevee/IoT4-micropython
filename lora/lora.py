from machine import UART
import utime

class rak811:
    ''' class to communicate with an ESP32 via serial AT commands to the RAK811 LoRa module '''
    
    def __init__(self, RxTxPort, baudrate, debug=False):
        self.RxTx = RxTxPort # RxTx channel of the ESP (1 or 2)
        self.bd = baudrate
        self.debug = debug
        self.version = ""
        self.serdev = None  # instance for UART
        
    def start(self):
        try:
            # make UART instance
            self.serdev = UART(self.RxTx, self.bd)
            # get version of LoRa board
            self.serdev.write(str.encode("at+version\r\n"))
            return self.isOK(20, "OK")
        
        except Exception as E:
            if self.debug:
                print("error on start UART", E)
            return "NOK"
        
    
    def stop(self):
        try:
            # only if UART instance exists
            if self.serdev != None:
                self.serdev.deinit()
                del self.serdev
                self.version = ""
            return "OK"
            
        except Exception as E:
            if self.debug:
                print("error on stop UART", E)
            return "NOK"
        
    
    def send(self):
        pass
    
    
    def recv(self):
        pass
    
    
    def getVersion(self):
        return self.version
    
    
    def getStatus(self):
        try:
            self.serdev.write(str.encode("at+get_config=lora:status\r\n"))
            return self.isOK(30, "List End")
        
        except Exception as E:
            if self.debug:
                print('Error on getStatus: ',E)
            return "NOK"
        
    
    def isOK(self, lines, stop):
        try:
            counter = 0
            while counter < lines:
                # wait a while before reading
                utime.sleep_ms(20)
                res = self.serdev.readline()
                # no answer
                if res == None:
                    counter += 1
                    continue
                # we did get an answer
                res = res.decode('utf-8')
                if self.debug:
                    print(res)
                # Is it OK ?
                if stop.upper() in res.upper():
                    return "OK"
                counter += 1
            # no answer after lines tries
            return "NOK"
        
        except Exception as E:
            if self.debug:
                print('Error on isOK: ',E)
            return "NOK"
            
        
        
            
