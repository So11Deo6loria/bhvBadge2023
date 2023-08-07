import lowpower
import utime
import machine


import _thread
import constants
import prettyLights
import hrMonitor
import cerealInterface

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
        self.startup()



    def startup(self):
        # self.sensor.setupSensor()
        self.leds.updateColorScheme("rainbow")
        self.leds.startupWave()
        self.leds.updateColorScheme('nathan')

        


    def runLoop(self):
        self.button = Pin(constants.BUTTON, Pin.IN, Pin.PULL_UP)
        self.button.irq(lambda e: print("button event!"), Pin.IRQ_FALLING)
        
        #startup Serial Interface
        serialInterface = cerealInterface.CerealInterface()
        _thread.start_new_thread(serialInterface.uartShell, ())
           
        # Hardware Configuration
        self.leds = prettyLights.LEDS()
        self.leds.wakeup()
        
        i2cHandle = SoftI2C(sda=Pin(constants.SDA_PIN), scl=Pin(constants.SCL_PIN), freq=constants.I2C_FREQ)
        self.sensor = hrMonitor.HRMonitor( i2cHandle, self.leds )

        self.startup()
        
        #giving sensor time to come
        self.sensor.configureHRSensor()
        
        startTime = utime.ticks_ms()
        while(True):
            currentTime = utime.ticks_ms()

            if((self.button.value() != 1) or (utime.ticks_diff(utime.ticks_ms(), startTime) > 60000)):
                print("getting sleepy")
                self.lowPowerPause()

            self.sensor.hrRunLoop()
            self.leds.tickHeartbeat()
            utime.sleep_ms(10)

Main()