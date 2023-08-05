import lowpower
import time


""" time.sleep(1)
DORMANT_PIN = 5
print("Pre-Trigger Start")
lowpower.dormant_with_modes({
        DORMANT_PIN: (lowpower.EDGE_LOW)
})
print("Triggered") """

import _thread
import constants
import prettyLights
import hrMonitor
import cerealInterface
import machine

from machine import Pin, Timer, SoftI2C


interrupt_flag = 0


def callback(self):
    global interrupt_flag
    print("Interrupt Detected")
    interrupt_flag=1
    
class Main:
    def __init__(self): 
        print("Start Up") # only print after receiving signal on Pin number DORMANT_PIN
        led = Pin(25, Pin.OUT)

        oldi2c1 = Pin(16,Pin.IN)
        oldi2c2 = Pin(17,Pin.IN)
        timer = Timer()

        def blink(timer):
            led.toggle()

        #timer.init(freq=5, mode=Timer.PERIODIC, callback=blink)        
        self.runLoop()

    def debugPrint(self, string):
        if( constants.DEBUG ):
            print( string )    

    def callback(self):
        global interrupt_flag
        print("Interrupt Detected")
        interrupt_flag=1

    def runLoop(self):
        # Default BPM
        global bpm 
        global interrupt_flag
        bpm = 90

        # GPIO Initialization
        # ledPin = Pin(constants.PICO_LED_PIN, Pin.OUT) # Can use this eventually
        oxPin = Pin(constants.OX_LED_PIN, Pin.OUT)
        deoxPin = Pin(constants.DEOX_LED_PIN, Pin.OUT)
        
        schemes = ["rainbow", "nathan", "heart", 'creepercrunch', 'cinnamontoastcrunch', 'applejacks']
        index = 0
        leds = prettyLights.LEDS()
        leds.updateColorScheme("rainbow")
        _thread.start_new_thread(leds.heartbeat, ())
    
        #Input for the Some Pin that was important. 
        pin = Pin(5, Pin.IN, Pin.PULL_DOWN)

        # pin.irq(trigger=Pin.IRQ_RISING, handler=callback)

        # while True:
        #     time.sleep(.5)
        #     print("checking")
        #     if pin.value() == 0:
        #        print(f"changing sheme to {schemes[index%(len(schemes)-1)]}")
        #        leds.updateColorScheme(schemes[index%(len(schemes)-1)]) # cycle through color schemes
        #        index+=1
        #        interrupt_flag=0

        # print("Setting Up Interrupt")

        # def callback(pin):
        #     print("Interrupt Detected")
        #     try:
        #         while( not ledClass.killLeds() ):
        #             time.sleep(0.05) # Dumb wait to make sure blink finishes
        #         machine.reset()
        #     except Exception as error:
        #         # handle the exception
        #         print("An exception occurred:", error)            



        # Enable Kill Switch
        # TODO        

        # if( constants.LED_TESTING ):

            # leds.heartbeat()
            # while True: 
            # #    for i in range(60, 100, 5):
            # #        ledClass.updateBPM(i)
            #     time.sleep(5)

            # cerealClass = cerealInterface.CerealInterface(oxPin, deoxPin)
            # while True:                                
            #     for cereal in constants.CEREAL_COLOR_SCHEMES:
            #         cerealClass.runCerealProfile("x")
            #         time.sleep(0.5)

        # Hardware Configuration

        cerealClass = cerealInterface.CerealInterface(oxPin, deoxPin)
        cerealClass.uartShell()

        i2cHandle = SoftI2C(sda=Pin(constants.SDA_PIN), scl=Pin(constants.SCL_PIN), freq=constants.I2C_FREQ)
        Sensor = hrMonitor.HRMonitor( i2cHandle, leds )

Main()