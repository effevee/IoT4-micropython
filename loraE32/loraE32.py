#######################################################################
# MicroPython class for EBYTE E32 Series LoRa modules which are based
# on SEMTECH SX1276/SX1278 chipsets and are available for 170, 433, 470,
# 868 and 915MHz frequencies in 100mW and 1W transmitting power versions.
# They all use a simple UART interface to control the device.
#
# Pin layout E32-868T20D (SX1276 868MHz 100mW DIP Wireless Module)
# +---------------------------------------------+
# | 0 - M0  (set mode)        [*]               |
# | 0 - M1  (set mode)        [*]               |
# | 0 - RXD (TTL UART input)  [*]               |
# | 0 - TXD (TTL UART output) [*]               |
# | 0 - AUX (status output)   [*]               |
# | 0 - VCC (3.3-5.2V)                          +---+
# | 0 - GND (GND)                                SMA| Antenna
# +-------------------------------------------------+
#     [*] ALL COMMUNICATION PINS ARE 3.3V !!!
#
# Transmission modes :
#   - Fixed : point to point - sender uses target address and target
#             channel of receiver
#   - Broadcast : sender uses 0xFFFF address and target channel, all
#             receivers this channel see the message
#   - Monitor : receiver with address of 0xFFFF or 0x0000 and target
#             channel will receive data from all senders with this channel
#
# Operating modes :
#   - 0=Normal (M0=0,M1=0) : UART and wireless open
#   - 1=wake up (M0=1,M1=0) : UART and wireless open, before transmit
#             receiver will be woken with preamble pulses
#   - 2=power save (M0=0,M1=1) : UART closed, wireless open, when
#             receiving data UART comes up to send the data to RXD pin
#   - 3=sleep (M0=1,M1=1) : sleep mode used to setup device
######################################################################

from machine import UART
import utime
import ujson


class ebyteE32:
    ''' class to interface an ESP32 via serial commands to the EBYTE
        E32 Series LoRa modules '''
    
    # UART ports
    PORT = { 'U1':1, 'U2':2 }
    # UART parity strings
    PARSTR = { '8N1':'00', '8O1':'01', '8E1':'10' }
    PARINV = { v:k for k, v in PARSTR.items() }
    # UART parity bits
    PARBIT = { 'N':None, 'E':0, 'O':1 }
    # UART baudrate
    BAUDRATE = { 1200:'000', 2400:'001', 4800:'010', 9600:'011',
                 19200:'100', 38400:'101', 57600:'110', 115200:'111' }
    BAUDRINV = { v:k for k, v in BAUDRATE.items() }
    # LoRa datarate
    DATARATE = { '0.3k':'000', '1.2k':'001', '2.4k':'010',
                 '4.8k':'011', '9.6k':'100', '19.2k':'101' }
    DATARINV = { v:k for k, v in DATARATE.items() }
    # Commands
    CMDS = { 'setConfigPwrDwnSave':0xC0,
             'getConfig':0xC1,
             'setConfigPwrDwnNoSave':0xC2,
             'getVersion':0xC3,
             'reset':0xC4 }
    # operation modes (set with M0 & M1)
    OPERMODE = { 'normal':'00', 'wakeup':'10', 'powersave':'01', 'sleep':'11' }
    # model frequency ranges (MHz)
    FREQ = { 170:[160, 170, 173], 400:[410, 470, 525], 433:[410, 433, 441],
             868:[862, 868, 893], 915:[900, 915, 931] }
    # model maximum transmision power
    # 20dBm = 100mW - 27dBm = 500 mW - 30dBm = 1000 mW (1 W)
    MAXPOW = { 'T20':0, 'T27':1, 'T30':2 }
    # transmission mode
    TRANSMODE = { 0:'transparent', 1:'fixed' }
    # IO drive mode
    IOMODE = { 0:'TXD AUX floating output, RXD floating input',
               1:'TXD AUX push-pull output, RXD pull-up input' }
    # wireless wakeup times from sleep mode
    WUTIME = { '000':'250ms', '001':'500ms', '010':'750ms', '011':'1000ms',
               '100':'1250ms', '101':'1500ms', '110':'1750ms', '111':'2000ms' }
    # Forward Error Correction (FEC) mode
    FEC = { 0:'off', 1:'on' }
    # transmission power T20/T27/T30 (dBm)
    TXPOWER = { '00':['20dBm', '27dBm', '30dBm'],
                '01':['17dBm', '24dBm', '27dBm'],
                '10':['14dBm', '21dBm', '24dBm'],
                '11':['10dBm', '18dBm', '21dBm'] }
    
    def __init__(self, Model='868T20D', Port='U1', Baudrate=9600, Parity='8N1', AirDataRate='2.4k', Address=0x0000, Channel=0x06, debug=False):
        ''' constructor for ebyte E32 LoRa module '''
        # configuration in json dictionary
        self.config = {}
        self.config['model'] = Model               # E32 model (default 868T20D)
        self.config['port'] = Port                 # UART channel on the ESP (U1 or U2)
        self.config['baudrate'] = Baudrate         # UART baudrate (default 9600)
        self.config['parity'] = Parity             # UART Parity (default 8N1)
        self.config['datarate'] = AirDataRate      # wireless baudrate (default 2.4k)
        self.config['address'] = Address           # target address (default 0x0000)
        self.config['channel'] = Channel           # target channel (default 0x06)
        self.config['frequency'] = 868             # base frequency for channel 6 (862 + 6 = 868MHz)
        self.config['transmode'] = 0               # transmission mode (default 0 - tranparent)
        self.config['iomode'] = 1                  # IO mode (default 1 - not floating)
        self.config['wutime'] = 0                  # wakeup time from sleep mode (default 0 - 250ms)
        self.config['fec'] = 1                     # forward error correction (default 1 - on)
        self.config['txpower'] = 0                 # trasmission power (default 0 - 20dBm/100mW)
        # save config to json file
        self.saveConfig2Json(self.config)
        # 
        self.debug = debug
        self.serdev = None             # instance for UART
        
    def start(self):
        try:
            # check parameters
            if self.config['port'] not in ebyteE32.PORT:
                self.config['port'] = 'U1'
            if self.config['baudrate'] not in ebyteE32.BAUDRATE:    
                self.config['baudrate'] = 9600
            if self.config['parity'] not in ebyteE32.PARSTR:
                self.config['parity'] = '8N1'
            if self.config['model'].split('T')[0] not in ebyteE32.FREQ:
                self.config['model'] = '868T20D'
            if self.config['datarate'] not in ebyteE32.DATARATE:
                self.config['datarate'] = '2.4k'
            # calculate frequency (= base frequency + channel * 1MHz)
HIER            freq = int(self.model.split('T')[0])
            self.frequency = ebyteE32.FREQ.get(freq)[0] + self.channel
            # make UART instance
            self.serdev = UART(ebyteE32.PORT.get(self.port))
            # init UART
            par = ebyteE32.PARBIT.get(str(self.parity)[1])
            self.serdev.init(baudrate=self.baudrate, bits=8, parity=par, stop=1)
            if self.debug:
                print(self.serdev)
            # get E32 config parameters
            res = self.getConfig()
            if res[0] == '0xC0':
                print('model       \tE32-%s'%(self.model))
                print('frequency   \t%dMhz'%(self.frequency))
                print('address     \t%s'%(res[1]))
                print('channel     \t%s'%(res[2]))
                print('datarate    \t%sbps'%(res[5]))                
                print('baudrate    \t%sbps'%(res[4]))
                print('parity      \t%s'%(res[3]))
                print('transmission\t%s'%(res[6]))
                print('IO mode     \t%s'%(res[7]))
                print('wakeup time \t%s'%(res[8]))
                print('FEC         \t%s'%(res[9]))
                print('TX power    \t%s'%(res[10]))
                return "OK"
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
            return "OK"
            
        except Exception as E:
            if self.debug:
                print("error on stop UART", E)
            return "NOK"
        
    
    def getVersion(self):
        ''' Get version info from the ebyte E32 LoRa module '''
        try:
            res = self.sendCommand('getVersion')
            if len(res) < 4:
                return "NOK"
            # decode result
            frequency = ebyteE32.FREQ.get(res[1],'unknown')
            version = res[2]
            features = res[3]
            return [frequency, version, features]
        
        except Exception as E:
            if self.debug:
                print('Error on getVersion: ',E)
            return "NOK"
        
    
    def getConfig(self):
        ''' Get config parameters from the ebyte E32 LoRa module '''
        try:
            HexCmd = [ebyteE32.CMDS.get('getConfig')]*3
            self.serdev.write(bytes(HexCmd))
            utime.sleep_ms(50)
            res = self.serdev.read()
            utime.sleep_ms(50)
            if len(res) < 6:
                return "NOK"
            # decode result
            lres = []
            lres = list(res)
            head = '0x{:02X}'.format(lres[0])
            addr = '0x{:04X}'.format(lres[1]*256+lres[2])
            # speed -> parity, baudrate, datarate
            bits = '{0:08b}'.format(lres[3])
            parstr = ebyteE32.PARINV.get(bits[0:2])
            baudrt = ebyteE32.BAUDRINV.get(bits[2:5])
            datart = ebyteE32.DATARINV.get(bits[5:])
            chan = '0x{:02X}'.format(lres[4])
            # option -> transmission, IO pullup, wakeup time, FEC, power
            bits = '{0:08b}'.format(lres[5])
            transm = ebyteE32.TRANSMODE.get(int(bits[0:1]))
            iomode = ebyteE32.IOMODE.get(int(bits[1:2]))
            wutime = ebyteE32.WUTIME.get(bits[2:5])
            fec = ebyteE32.FEC.get(int(bits[5:6]))
            devmaxp = ebyteE32.MAXPOW.get(self.model[3:6], 0)
            txpower = ebyteE32.TXPOWER.get(bits[6:])[devmaxp]
            return [head, addr, chan, parstr, baudrt, datart, transm, iomode, wutime,fec, txpower]

        except Exception as E:
            if self.debug:
                print('Error on getConfig: ',E)
            return "NOK"  
    

    def saveConfig2Json(self, config):
        ''' Save config parametes to JSON file ''' 
        # dump dictionary to json file
        with open('E32config.json', 'w') as outfile:  
            ujson.dump(config, outfile)    
