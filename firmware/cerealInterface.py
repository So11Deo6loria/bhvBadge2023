import time
import constants
from neopixel import NeoPixel

class CerealInterface:
  def __init__(self, pin1, pin2):
    print("Cereal Init")
    self.pin1 = NeoPixel( pin1, 8 )
    self.pin2 = NeoPixel( pin2, 8 )

  def hexListToRGBTupleList( self, cerealArray ):
    colorArray = []
    for cerealHexValue in cerealArray:
      colorArray.append(tuple(bytearray.fromhex(cerealHexValue)))
    return colorArray

  def runCerealProfile(self, cereal):
    print("Running Cereal Profile: " + cereal)

    if( cereal in constants.CEREAL_COLOR_SCHEMES ):
      cerealArray = constants.CEREAL_COLOR_SCHEMES[cereal]
      colorArray = self.hexListToRGBTupleList( cerealArray )
    
      ledArray = [constants.LED_OFF] * ( constants.LED_COUNT * 2 )
      shiftArray = ledArray + colorArray
      shiftArray.reverse()

      for element in shiftArray:
        ledArray.insert(0, element)
        for led in range(constants.LED_COUNT*2):
          if( led < constants.LED_COUNT ):
            self.pin2[led] = ledArray[led]
          else:
            self.pin1[(led - constants.LED_COUNT)] = ledArray[led]
        self.pin1.write()  
        self.pin2.write()
        time.sleep(constants.CEREAL_DELAY)

      #ledArray = [constants.LED_OFF] * constants.LED_COUNT        

      #for element in shiftArray:
      #  ledArray.insert(0, element)
      #  for led in range(constants.LED_COUNT):
      #    self.pin1[led] = ledArray[led]
      #  self.pin1.write()
      #  time.sleep(constants.CEREAL_DELAY)        
    else:
      print("Unsupported Cereal....")