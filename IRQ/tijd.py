from simpleWifi import Wifi
from ntptime import settime
from machine import RTC
import utime

class LocalTime:
    ''' Ophalen lokale tijd van ntpserver '''
    
    def __init__(self, offset, debug=False):
        self.__offset = offset
        self.__tryTimes = 5
        self.debug = debug
        self.wf = None
        
    def startInternetTime(self):
        try:
            # wifi verbinding maken
            self.wf = Wifi()
            # wifi verbinding niet gelukt
            if not self.wf.open():
                return (-1, -1)
            # init klok ESP32 met UTC tijd van ntpserver 
            tries = 0
            while tries < self.__tryTimes:
                try:
                    utime.sleep(1)
                    settime()
                    break
                except:
                    tries += 1
                    utime.sleep(1)
            # wifi verbinding sluiten
            self.wf.close()
            # is de klok upgedate ?
            if tries < self.__tryTimes:
                return (0, 1)
            else:
                return (-1, -1)
        except Exception as E:
            if self.debug:
                print('fout bij ophalen van internet tijd', E)
            return (-1, -1)
        
    def getLocalTime(self):
        try:
            # RTC klok initialiseren
            rtc = RTC()
            if self.debug:
                print(rtc.datetime())
            # locale tijd met correctie offset als tuple
            lt = utime.localtime(utime.mktime(utime.localtime()) + self.__offset*3600)
            if self.debug:
                print(lt)
            # locale tijd omzetten naar string
            lts = '{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(lt[0], lt[1], lt[2], lt[3], lt[4], lt[5])
            return (0, lts)
        except Exception as E:
            if self.debug:
                print('fout bij ophalen locale tijd', E)
            return (-1, -1)
    
        