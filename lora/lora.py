from machine import UART

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
            # try 5 times maximum 
            counter = 0
            while counter < 5:
                res = self.serdev.readline()
                # no answer
                if res == None:
                    counter += 1
                    continue
                # we did get an answer
                res = res.decode('utf-8')
                # Is it OK ?
                if "OK" in res.upper():
                    self.version = res
                    return "OK"
                counter += 1
            # no answer after 5 tries
            return "NOK"
        
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
            
