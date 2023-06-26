import lowpower
import time

time.sleep(0.25)
DORMANT_PIN = 5
print("Pre-Trigger Start")
lowpower.dormant_with_modes({
        DORMANT_PIN: (lowpower.EDGE_LOW)
})
print("Triggered")

import _thread

import constants
import leds
import hrMonitor
import cerealInterface
import machine

from machine import Pin, Timer, SoftI2C

class Main:
    def __init__(self): 
        print("Start Up") # only print after receiving signal on Pin number DORMANT_PIN
        led = Pin(25, Pin.OUT)
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
        interrupt_flag=1
        print("Interrupt has occured")

    def runLoop(self):
        # Default BPM
        global bpm 
        bpm = 90

        # GPIO Initialization
        ledPin = Pin(constants.PICO_LED_PIN, Pin.OUT) # Can use this eventually
        oxPin = Pin(constants.OX_LED_PIN, Pin.OUT)
        deoxPin = Pin(constants.DEOX_LED_PIN, Pin.OUT)
        ledClass = leds.LEDS(oxPin, deoxPin, bpm)

        print("Setting Up Interrupt")
        pin = Pin(5, Pin.IN, Pin.PULL_DOWN)

        def callback(pin):
            print("Interrupt Detected")
            try:
                while( not ledClass.killLeds() ):
                    time.sleep(0.05) # Dumb wait to make sure blink finishes
                machine.reset()
            except Exception as error:
                # handle the exception
                print("An exception occurred:", error)            

        pin.irq(trigger=Pin.IRQ_RISING, handler=callback)


        # Enable Kill Switch
        # TODO        

        if( constants.LED_TESTING ):
            #_thread.start_new_thread(ledClass.heartbeat, ())
            ledClass.heartbeat()
            #while True: 
            #    for i in range(60, 100, 5):
            #        ledClass.updateBPM(i)
            #        time.sleep(5)

            cerealClass = cerealInterface.CerealInterface(oxPin, deoxPin)
            while True:                                
                for cereal in constants.CEREAL_COLOR_SCHEMES:
                    cerealClass.runCerealProfile("x")
                    time.sleep(0.5)

        # Hardware Configuration
        i2cHandle = SoftI2C(sda=Pin(constants.SDA_PIN), scl=Pin(constants.SCL_PIN), freq=constants.I2C_FREQ)
        hrSensor = hrMonitor.HRMonitor( i2cHandle, ledClass )

Main()