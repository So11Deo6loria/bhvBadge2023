import lowpower
import utime
import machine


import _thread
import constants
import prettyLights
import hrMonitor
import cerealInterface


import ujson


from machine import Pin, Timer, SoftI2C
class Main:
    def __init__(self): 
        print("Start Up") # only print after receiving signal on Pin number DORMANT_PIN

        oldi2c1 = Pin(16,Pin.IN)
        oldi2c2 = Pin(17,Pin.IN)
        self.runLoop()
   
    def lowPowerPause(self):
        self.sensor.shutdown()
        self.leds.shutdown()
        while(self.button.value() != 1):
            utime.sleep_ms(10)
        lowpower.dormant_until_pin(constants.BUTTON)
        self.sensor.wakeUp()
        self.leds.wakeup()

    def startupAnimation(self):
        # self.sensor.setupSensor()
        self.leds.updateColorScheme(self.startupColor)
        self.leds.startupWave()
        self.leds.updateColorScheme(self.heartbeatColor)

    def read_config(self):
        try:
            with open('config.json', 'r') as f:
                data = ujson.load(f)
                return data
        except:
            return False
    def runLoop(self):

        config = self.read_config()
        if(config):
            print("Loading following configuration:")
            print(config)
            self.startupColor = config['startupColor']
            self.heartbeatColor = config['heartbeatColor']
            self.sleepTimeout = config['sleepTimeout']
        else:
            print("Loading default configuration")
            self.startupColor = 'heart',
            self.heartbeatColor = 'heart'
            self.sleepTimeout = 300 # 300 seconds 


        self.button = Pin(constants.BUTTON, Pin.IN, Pin.PULL_UP)
        self.button.irq(lambda e: print("button event!"), Pin.IRQ_FALLING)
        
        #startup Serial Interface
        serialInterface = cerealInterface.CerealInterface()
        _thread.start_new_thread(serialInterface.uartShell, ())
           
        #Initialize LED Manager and Turn on Power
        self.leds = prettyLights.LEDS()
        self.leds.wakeup()

        #Initialize HW for HR Sensor        


        i2cHandle = SoftI2C(sda=Pin(constants.SDA_PIN), scl=Pin(constants.SCL_PIN), freq=constants.I2C_FREQ)
        self.sensor = hrMonitor.HRMonitor( i2cHandle, self.leds )
                 
        #Give sensor time to come with a sexy animation
        self.leds.updateColorScheme(self.startupColor)
        self.leds.startupWave()
        self.leds.updateColorScheme(self.heartbeatColor)

        #Configure Sensor
        self.sensor.configureHRSensor()
        
        #Capture the Bootup Time    
        startTime = utime.ticks_ms()

        while(True):
            currentTime = utime.ticks_ms()

            if((self.button.value() != 1) or (utime.ticks_diff(utime.ticks_ms(), startTime) > int(self.sleepTimeout)*1000)):
                print("getting sleepy")
                self.lowPowerPause()
                startTime = utime.ticks_ms()
                self.startupAnimation()

            self.sensor.hrRunLoop()
            self.leds.tickHeartbeat()
            utime.sleep_ms(10)

Main()