import time
import constants
from neopixel import NeoPixel

class LEDS:  
  global timeDelay
  oxHeartProfile = []
  deoxHeartProfile = []
  oxLEDArray = [constants.LED_OFF] * constants.LED_COUNT
  deoxLEDArray = [constants.LED_OFF] * constants.LED_COUNT

  def __init__(self, pin1, pin2, bpm):
    # This feels dumb
    self.oxLed = NeoPixel(pin1, 8)
    self.deoxLed = NeoPixel(pin2, 8)
    self.bpm = bpm
    self.threadActive = True
    self.createHeartbeatProfiles()

  def createHeartbeatProfiles(self):
    oxColorArray = []
    deoxColorArray = []
    for intensity in constants.HEART_PATTERN:
      colorIntensity = round(intensity * constants.HEART_LED_INTENSITY)
      oxColorArray.append(tuple([colorIntensity, 0, 0]))
      deoxColorArray.append(tuple([0, 0, colorIntensity]))    
    LEDS.oxHeartProfile = LEDS.oxLEDArray + oxColorArray
    LEDS.oxHeartProfile.reverse()
    LEDS.deoxHeartProfile = LEDS.deoxLEDArray + deoxColorArray
    LEDS.deoxHeartProfile.reverse()

  def updateBPM(self, bpm):
    self.bpm = bpm 

  def disableThread(self):
    self.threadActive = False

  def enableThread(self):
    self.threadActive = True

  def killLeds(self):
    for led in range(7): 
      self.oxLed[led] = constants.LED_OFF
      self.deoxLed[led] = constants.LED_OFF
    self.oxLed.write()      
    self.deoxLed.write()
    return True    
      
  def heartbeat(self):   
    while( True ):
      if( self.bpm > 50 and self.bpm < 200 ):
        timeDelay = (1/(self.bpm/60))

      if( self.threadActive == True ):
        # May need to confirm the length of the shift arrays are the same
        for index in range(len(LEDS.oxHeartProfile)): 
          LEDS.oxLEDArray.insert(0, LEDS.oxHeartProfile[index])
          LEDS.deoxLEDArray.insert(0, LEDS.deoxHeartProfile[index])

          for led in range(constants.LED_COUNT):
            self.oxLed[led] = LEDS.oxLEDArray[led]
            self.deoxLed[led] = LEDS.deoxLEDArray[led]
          self.oxLed.write()
          self.deoxLed.write()
          time.sleep(constants.BLINK_DELAY)
        time.sleep(timeDelay)

  def testNewHeartbeat(self):
    oxColorArray = []
    deoxColorArray = []
    oxLEDArray = [constants.LED_OFF] * 4
    deoxLEDArray = [constants.LED_OFF] * 4
    for intensity in constants.HEART_PATTERN:
      colorIntensity = round(intensity * constants.HEART_LED_INTENSITY)
      oxColorArray.append(tuple([colorIntensity, 0, 0]))
      deoxColorArray.append(tuple([0, 0, colorIntensity]))    
    LEDS.oxHeartProfile = oxLEDArray + oxColorArray
    LEDS.oxHeartProfile.reverse()
    LEDS.deoxHeartProfile = deoxLEDArray + deoxColorArray
    LEDS.deoxHeartProfile.reverse()

    while( True ):
      if( self.bpm > 50 and self.bpm < 200 ):
        timeDelay = (1/(self.bpm/60))

      if( self.threadActive == True ):
        # May need to confirm the length of the shift arrays are the same
        for index in range(len(LEDS.oxHeartProfile)): 
          LEDS.oxLEDArray.insert(0, LEDS.oxHeartProfile[index])
          LEDS.deoxLEDArray.insert(0, LEDS.deoxHeartProfile[index])

          for led in range(constants.LED_COUNT):
            self.oxLed[led] = LEDS.oxLEDArray[led]
            self.deoxLed[led] = LEDS.deoxLEDArray[led]
          self.oxLed.write()
          self.deoxLed.write()
          time.sleep(constants.BLINK_DELAY)
        time.sleep(timeDelay)        