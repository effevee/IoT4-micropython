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
# | 0 - AUX (device status)   [*]               |
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

from machine import Pin, UART
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
    # version info frequency
    FREQV = { '0x32':433, '0x38':470, '0x45':868, '0x44':915, '0x46':170 }
    # model maximum transmision power
    # 20dBm = 100mW - 27dBm = 500 mW - 30dBm = 1000 mW (1 W)
    MAXPOW = { 'T20':0, 'T27':1, 'T30':2 }
    # transmission mode
    TRANSMODE = { 0:'broadcast', 1:'fixed' }
    # IO drive mode
    IOMODE = { 0:'TXD AUX floating output, RXD floating input',
               1:'TXD AUX push-pull output, RXD pull-up input' }
    # wireless wakeup times from sleep mode
    WUTIME = { 0b000:'250ms', 0b001:'500ms', 0b010:'750ms', 0b011:'1000ms',
               0b100:'1250ms', 0b101:'1500ms', 0b110:'1750ms', 0b111:'2000ms' }
    # Forward Error Correction (FEC) mode
    FEC = { 0:'off', 1:'on' }
    # transmission power T20/T27/T30 (dBm)
    TXPOWER = { 0b00:['20dBm', '27dBm', '30dBm'],
                0b01:['17dBm', '24dBm', '27dBm'],
                0b10:['14dBm', '21dBm', '24dBm'],
                0b11:['10dBm', '18dBm', '21dBm'] }
    

    def __init__(self, PinM0, PinM1, PinAUX, Model='868T20D', Port='U1', Baudrate=9600, Parity='8N1', AirDataRate='2.4k', Address=0x0000, Channel=0x06, debug=False):
        ''' constructor for ebyte E32 LoRa module '''
        # configuration in dictionary
        self.config = {}
        self.config['model'] = Model               # E32 model (default 868T20D)
        self.config['port'] = Port                 # UART channel on the ESP (default U1)
        self.config['baudrate'] = Baudrate         # UART baudrate (default 9600)
        self.config['parity'] = Parity             # UART Parity (default 8N1)
        self.config['datarate'] = AirDataRate      # wireless baudrate (default 2.4k)
        self.config['address'] = Address           # target address (default 0x0000)
        self.config['channel'] = Channel           # target channel (0-31, default 0x06)
        self.calcFrequency()                       # calculate frequency (min frequency + channel*1 MHz)
        self.config['transmode'] = 0               # transmission mode (default 0 - tranparent)
        self.config['iomode'] = 1                  # IO mode (default 1 = not floating)
        self.config['wutime'] = 0                  # wakeup time from sleep mode (default 0 = 250ms)
        self.config['fec'] = 1                     # forward error correction (default 1 = on)
        self.config['txpower'] = 0                 # transmission power (default 0 = 20dBm/100mW)
        # 
        self.PinM0 = PinM0                         # M0 pin number
        self.PinM1 = PinM1                         # M1 pin number
        self.PinAUX = PinAUX                       # AUX pin number
        self.M0 = None                             # instance for M0 Pin (set operation mode)
        self.M1 = None                             # instance for M1 Pin (set operation mode)
        self.AUX = None                            # instance for AUX Pin (device status : 0=busy - 1=idle)
        self.serdev = None                         # instance for UART
        self.debug = debug
        

    def start(self):
        ''' Start the ebyte E32 LoRa module '''
        try:
            # check parameters
            if int(self.config['model'].split('T')[0]) not in ebyteE32.FREQ:
                self.config['model'] = '868T20D'
            if self.config['port'] not in ebyteE32.PORT:
                self.config['port'] = 'U1'
            if int(self.config['baudrate']) not in ebyteE32.BAUDRATE:    
                self.config['baudrate'] = 9600
            if self.config['parity'] not in ebyteE32.PARSTR:
                self.config['parity'] = '8N1'
            if self.config['datarate'] not in ebyteE32.DATARATE:
                self.config['datarate'] = '2.4k'
            if self.config['channel'] > 31:
                self.config['channel'] = 31
            # make UART instance
            self.serdev = UART(ebyteE32.PORT.get(self.config['port']))
            # init UART
            par = ebyteE32.PARBIT.get(str(self.config['parity'])[1])
            self.serdev.init(baudrate=self.config['baudrate'], bits=8, parity=par, stop=1)
            if self.debug:
                print(self.serdev)
            # make operation mode & device status instances
            self.M0 = Pin(self.PinM0, Pin.OUT)
            self.M1 = Pin(self.PinM1, Pin.OUT)
            self.AUX = Pin(self.PinAUX, Pin.IN, Pin.PULL_UP)
            if self.debug:
                print(self.M0, self.M1, self.AUX)
            # set config to the ebyte E32 LoRa module
            self.setConfig('setConfigPwrDwnSave')
            # save config to json file
            self.saveConfigToJson()
            return "OK"
        
        except Exception as E:
            if self.debug:
                print("error on start UART", E)
            return "NOK"
        
    
    def sendMessage(self, address, channel, message):
        ''' Send the message to ebyte E32 LoRa modules with this address and channel.
            if the address is 0xFFFF or 0x0000, the message is broadcasted to all modules with this channel'''
        try:
            # type of message ?
            if address in [0x0000, 0xFFFF]:   # broadcast
                self.setTransmissionMode(0)
            else:                             # point to point 
                self.setTransmissionMode(1)
            # channel/frequency
            # self.setChannel(channel)
            # put into wakeup mode (includes preamble signals to wake up device in powersave or sleep mode)
            self.setOperationMode('wakeup')
            self.waitForDeviceIdle()
            # encode message
            msg = []
            msg.append(address//256)          # high address byte
            msg.append(address%256)           # low address byte
            msg.append(channel)               # channel
            for i in range(len(message)):     # message
                msg.append(ord(message[i]))   # ascii code of character
            # debug
            if self.debug:
                print(msg)
            # send the message
            self.serdev.write(bytes(msg))
            return "OK"
        
        except Exception as E:
            if self.debug:
                print('Error on sendMessage: ',E)
            return "NOK"
        
        
    def recvMessage(self, address, channel):
        ''' Receive messages from ebyte E32 LoRa modules with this address and channel.
            if the address is 0xFFFF or 0x0000, receives messages from all modules with this channel'''
        try:
            # type of message ?
            if address in [0x0000, 0xFFFF]:   # broadcast
                self.setTransmissionMode(0)
            else:                             # point to point 
                self.setTransmissionMode(1)    
            # put into normal mode
            self.setOperationMode('normal')
            self.waitForDeviceIdle()
            # receive message
            message = self.serdev.read()
            # debug
            if self.debug:
                print(message)
            # decode message
            '''msg = []
            msg.append(address//256)          # high address byte
            msg.append(address%256)           # low address byte
            msg.append(channel)               # channel
            for i in range(len(message)):     # message
                msg.append(ord(message[i]))   # ascii code of character  '''
            return "OK"
        
        except Exception as E:
            if self.debug:
                print('Error on recvMessage: ',E)
            return "NOK"
        pass        

    
    def reset(self):
        ''' Reset the ebyte E32 Lora module '''
        try:
            # send the command
            res = self.sendCommand('reset')
            # discard result
            return "OK"
          
        except Exception as E:
            if self.debug:
                print("error on reset", E)
            return "NOK"


    def stop(self):
        ''' Stop the ebyte E32 LoRa module '''
        try:
            if self.serdev != None:
                self.serdev.deinit()
                del self.serdev
            return "OK"
            
        except Exception as E:
            if self.debug:
                print("error on stop UART", E)
            return "NOK"
        
    
    def sendCommand(self, command):
        ''' Send a command to the ebyte E32 LoRa module.
            The module has to be in sleep mode '''
        try:
            # put into sleep mode
            self.setOperationMode('sleep')
            self.waitForDeviceIdle()
            # send command
            HexCmd = ebyteE32.CMDS.get(command)
            if HexCmd in [0xC0, 0xC2]:        # set config to device
                header = HexCmd
                HexCmd = self.encodeConfig()
                HexCmd[0] = header
            else:                             # get config, get version, reset
                HexCmd = [HexCmd]*3
            if self.debug:
                print(HexCmd)
            self.serdev.write(bytes(HexCmd))
            self.waitForDeviceIdle()
            # read result
            if command == 'reset':
                result = ''
            else:
                result = self.serdev.read()
                if self.debug:
                    print(result)
                self.waitForDeviceIdle()            
            return result
        
        except Exception as E:
            if self.debug:
                print('Error on sendCommand: ',E)
            return "NOK"
        
        
    
    def getVersion(self):
        ''' Get the version info from the ebyte E32 LoRa module '''
        try:
            # send the command
            res = self.sendCommand('getVersion')
            # check result
            if len(res) != 4:
                return "NOK"
            # decode result
            freq = ebyteE32.FREQV.get(hex(res[1]),'unknown')
            # show version
            if res[0] == 0xc3:
                print('=================== VERSION ====================')
                print('frequency   \t%dMhz'%(freq))
                print('version     \t%d'%(res[2]))
                print('features    \t%d'%(res[3]))
                print('================================================')
            return "OK"
        
        except Exception as E:
            if self.debug:
                print('Error on getVersion: ',E)
            return "NOK"
        
    
    def getConfig(self):
        ''' Get config parameters from the ebyte E32 LoRa module '''
        try:
            # send the command
            res = self.sendCommand('getConfig')
            # check result
            if len(res) != 6:
                return "NOK"
            # decode result
            self.decodeConfig(res)
            # show config
            self.showConfig()
            return "OK"

        except Exception as E:
            if self.debug:
                print('Error on getConfig: ',E)
            return "NOK"  
    

    def decodeConfig(self, message):
        ''' decode the config message from the ebyte E32 LoRa module to update the config dictionary '''
        # message byte 0 = header
        header = int(message[0])
        # message byte 1 & 2 = address
        self.config['address'] = int(message[1])*256 + int(message[2])
        # message byte 3 = speed (parity, baudrate, datarate)
        bits = '{0:08b}'.format(message[3])
        self.config['parity'] = ebyteE32.PARINV.get(bits[0:2])
        self.config['baudrate'] = ebyteE32.BAUDRINV.get(bits[2:5])
        self.config['datarate'] = ebyteE32.DATARINV.get(bits[5:])
        # message byte 4 = channel
        self.config['channel'] = int(message[4])
        # message byte 5 = option (transmode, iomode, wutime, fec, txpower)
        bits = '{0:08b}'.format(message[5])
        self.config['transmode'] = int(bits[0:1])
        self.config['iomode'] = int(bits[1:2])
        self.config['wutime'] = int(bits[2:5])
        self.config['fec'] = int(bits[5:6])
        self.config['txpower'] = int(bits[6:])
        
    
    def encodeConfig(self):
        ''' encode the config dictionary to create the config message of the ebyte E32 LoRa module '''
        # Initialize config message
        message = []
        # message byte 0 = header
        message.append(0xC0)
        # message byte 1 = high address
        message.append(self.config['address']//256)
        # message byte 2 = low address
        message.append(self.config['address']%256)
        # message byte 3 = speed (parity, baudrate, datarate)
        bits = '0b'
        bits += ebyteE32.PARSTR.get(self.config['parity'])
        bits += ebyteE32.BAUDRATE.get(self.config['baudrate'])
        bits += ebyteE32.DATARATE.get(self.config['datarate'])
        message.append(int(bits))
        # message byte 4 = channel
        message.append(self.config['channel'])
        # message byte 5 = option (transmode, iomode, wutime, fec, txpower)
        bits = '0b'
        bits += str(self.config['transmode'])
        bits += str(self.config['iomode'])
        bits += '{0:03b}'.format(self.config['wutime'])
        bits += str(self.config['fec'])
        bits += '{0:02b}'.format(self.config['txpower'])
        message.append(int(bits))
        return message
    

    def showConfig(self):
        ''' Show the config parameters of the ebyte E32 LoRa module on the shell '''
        print('=================== CONFIG =====================')
        print('model       \tE32-%s'%(self.config['model']))
        print('frequency   \t%dMhz'%(self.config['frequency']))
        print('address     \t%s'%(hex(self.config['address'])))
        print('channel     \t%s'%(hex(self.config['channel'])))
        print('datarate    \t%sbps'%(self.config['datarate']))                
        print('port        \t%s'%(self.config['port']))
        print('baudrate    \t%dbps'%(self.config['baudrate']))
        print('parity      \t%s'%(self.config['parity']))
        print('transmission\t%s'%(ebyteE32.TRANSMODE.get(self.config['transmode'])))
        print('IO mode     \t%s'%(ebyteE32.IOMODE.get(self.config['iomode'])))
        print('wakeup time \t%s'%(ebyteE32.WUTIME.get(self.config['wutime'])))
        print('FEC         \t%s'%(ebyteE32.FEC.get(self.config['fec'])))
        maxp = ebyteE32.MAXPOW.get(self.config['model'][3:6], 0)
        print('TX power    \t%s'%(ebyteE32.TXPOWER.get(self.config['txpower'])[maxp]))
        print('================================================')


    def waitForDeviceIdle(self):
        ''' Wait for the E32 LoRa module to become idle (AUX pin high) '''
        utime.sleep_ms(100)
        
            
    def saveConfigToJson(self):
        ''' Save config dictionary to JSON file ''' 
        with open('E32config.json', 'w') as outfile:  
            ujson.dump(self.config, outfile)    


    def loadConfigFromJson(self):
        ''' Load config dictionary from JSON file ''' 
        with open('E32config.json', 'r') as infile:
            result = ujson.load(infile)
        print(self.config)
        
    
    def calcFrequency(self):
        ''' Calculate the frequency (= minimum frequency + channel * 1MHz)''' 
        # get minimum and maximum frequency
        freqkey = int(self.config['model'].split('T')[0])
        minfreq = ebyteE32.FREQ.get(freqkey)[0]
        maxfreq = ebyteE32.FREQ.get(freqkey)[2]
        # calculate frequency
        freq = minfreq + self.config['channel']
        if freq > maxfreq:
            self.config['frequency'] = maxfreq
            self.config['channel'] = hex(maxfreq - minfreq)
        else:
            self.config['frequency'] = freq

        
    def setFrequency(self, frequency):
        ''' Set the frequency of the ebyte E32 LoRa module '''
        if frequency != self.config['frequency']:
            self.config['frequency'] = frequency
            self.setConfig('setConfigPwrDwnSave')
        
        
    def setAddress(self, address):
        ''' Set the address of the E32 LoRa module '''
        if address != self.config['address']:
            self.config['address'] = address
            self.setConfig('setConfigPwrDwnSave')
    
    
    def setChannel(self, channel):
        ''' Set the channel of the E32 LoRa module '''
        if channel != self.config['channel']:
            self.config['channel'] = channel
            self.calcFrequency()
            self.setConfig('setConfigPwrDwnSave')
    
    
    def setTransmissionMode(self, transmode):
        ''' Set the transmission mode of the E32 LoRa module '''
        if transmode != self.config['transmode']:
            self.config['transmode'] = transmode
            self.setConfig('setConfigPwrDwnSave')
            
            
    def setConfig(self, save_cmd):
        ''' Set config parameters for the ebyte E32 LoRa module '''
        try:
            # send the command
            res = self.sendCommand(save_cmd)
            # check result
            if len(res) != 6:
                return "NOK"
            # decode result
            self.decodeConfig(res)
            # show config
            self.showConfig()
            # save config to json file
            self.saveConfigToJson()
            return "OK"
        
        except Exception as E:
            if self.debug:
                print('Error on setConfig: ',E)
            return "NOK"  


    def setOperationMode(self, mode):
        ''' Set operation mode of the E32 LoRa module '''
        # wait for the device to become idle
        self.waitForDeviceIdle()
        # get operation mode settings (default normal)
        bits = ebyteE32.OPERMODE.get(mode, '00')
        # set operation mode
        self.M0.value(int(bits[0]))
        self.M1.value(int(bits[1]))
    

    