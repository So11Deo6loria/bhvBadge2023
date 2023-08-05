import time
import constants
from neopixel import NeoPixel
import machine
import math
from machine import Pin, Timer, SoftI2C


class LEDS:  
  global timeDelay
  colorScheme = 'heart'
  colorSchemes = {
  'heart':
  ['0000ff','0000ff','0000ff','0000ff','0000ff','0000ff','0000ff',
   'ff0000','ff0000','ff0000','ff0000','ff0000','ff0000','ff0000'],

  'nathan':
  ['00ff00','00ff00','00ff00','00ff00','00ff00','00ff00','00ff00', 
   '0000ff','0000ff','0000ff','00006f','0000ff','0000ff','0000ff'],

  'cinnamontoastcrunch': 
  ['ce9958','ce9958','724705','724705','d8d09f','d8d09f','d8d09f',
   'ce9958','b8732d','b8732d','b8732d','9f633b','9f633b','9f633b'],
  
  'fruitypebbles':
  ['f0aa37','ffd52b','00ffd7','2edfb4','10b990','9476d6','f23333', 
   '9476d6','d65a8a','00ffd7','2edfb4','9476d6','f23333','f23333'],  
  'luckycharms':
  ['216209', '8fac06', 'bdd9a3', '56a20d', '91d521'],
  'fruitloops':
  ['ff0000', 'ffe700', '7cff00', 'c900ff', '00dfff'],
  
  'trix':
  ['58e3ff', '87a2ff', 'af7ffc', 'da4e7d', 'f14848'], 
  
  'rainbow':
  ['ff008f', 'ff00ff', '0010ff', '00cfff', '00ff00', 'ff5500', 'ff1500',
   'ff00ff', '0020ff', '00cfff', '00ff00', 'ffaf00', 'ff1500','ff0000',],

  'applejacks':
  ['3cbf2e', 'e88f23', '7a4606', '3cbf2e', 'e88f23', '7a4606', '3cbf2e', 
   'e88f23', '7a4606', '3cbf2e', 'e88f23', '7a4606', '3cbf2e', 'e88f23'],

   'oreo':
   ['f2f0ed','171716'],

   'booberry':
   ['8362a6','68bce3','4a7e96','fc0505'],

    'creepercrunch':
   ['8fe38f','0f800f','0db50d','609e60','004500'],

   'reesespuffs':
   ['fe5200','551e0a','fdef14'],

   'carmellacreeper':
   ['22b32c','a2b322','e56fed','ed6fb7'],

   'frankenberry':
   ['ed6fb7','6fc1ed','cf84f0','e5dfe8']
}

  # ledConfig = [ \
  #   {'startTime': 0.6284, 'pulseWidth': 0.608}, #1
  #   {'startTime': 0.6412, 'pulseWidth': 0.6421}, #2
  #   {'startTime': 0.0885, 'pulseWidth': 0.6541}, #3
  #   {'startTime': 0.2585, 'pulseWidth': 0.4541}, #4
  #   {'startTime': 0.5580, 'pulseWidth': 0.2545}, #5
  #   {'startTime': 0.5223, 'pulseWidth': 0.4670}, #6
  #   {'startTime': 0.6200, 'pulseWidth': 0.2656}, #7
  #   {'startTime': 0.6712, 'pulseWidth': 0.7981}, #8
  #   {'startTime': 0.0885, 'pulseWidth': 0.6541}, #9
  #   {'startTime': 0.2509, 'pulseWidth': 0.5116}, #10
  #   {'startTime': 0.5513, 'pulseWidth': 0.4526}, #11
  #   {'startTime': 0.5723, 'pulseWidth': 0.4660}, #12
  #   {'startTime': 0.5862, 'pulseWidth': 0.4656}, #13
  #   {'startTime': 0.6232,	'pulseWidth': 0.4656}] #14
  
  ledConfig = [ \
    {'startTime': 0.84584, 'pulseWidth': 0.4508}, #1
    {'startTime': 0.8712, 'pulseWidth': 0.6581}, #2
    {'startTime': 0.1585, 'pulseWidth': 0.4541}, #3
    {'startTime': 0.2585, 'pulseWidth': 0.3041}, #4
    {'startTime': 0.45080, 'pulseWidth': 0.445}, #5
    {'startTime': 0.5223, 'pulseWidth': 0.4670}, #6
    {'startTime': 0.6000, 'pulseWidth': 0.3256}, #7
    {'startTime': 0.8712, 'pulseWidth': 0.6581}, #8
    {'startTime': 0.1585, 'pulseWidth': 0.4541}, #9
    {'startTime': 0.2589, 'pulseWidth': 0.3016}, #10
    {'startTime': 0.4513, 'pulseWidth': 0.442}, #11
    {'startTime': 0.5723, 'pulseWidth': 0.2660}, #12
    {'startTime': 0.5862, 'pulseWidth': 0.2656}, #13
    {'startTime': 0.6032,	'pulseWidth': 0.3256}] #14
  
  def __init__(self):
    # This feels dumb

    deoxPin = Pin(18, Pin.OUT)
    ledDataPin = Pin(19, Pin.OUT)
    ledControl = Pin( 25, Pin.OUT)
    ledPower = Pin( 22, Pin.OUT)
    ledPower.on()
    self.strand = NeoPixel(ledDataPin, 7) #[0]*7 
    #
    self.strand2 = NeoPixel(deoxPin, 7) # [0]*7
    self.bpm = 100
    self.colorScheme = "heart"
    self.ledBaseColors = [[0]*3]*14

    self.updateColorScheme(self.colorScheme)
  
  def killLeds(self):
    for led in range(7): 
      self.oxLed[led] = tuple([0,0,0])
      self.deoxLed[led] = tuple([0,0,0])
    self.oxLed.write()      
    self.deoxLed.write()
    return True    

  def updateBPM( self, newBPM ):
    self.bpm = newBPM

  def updateColorScheme( self, newColorScheme ):
    self.colorScheme = newColorScheme
        
    #sets up a base color list/array thats easier to work with from the generic hex values that are easier to edit.  Done only on change for efficiency...
    if newColorScheme in self.colorSchemes:
      for index, color in enumerate(self.colorSchemes[newColorScheme]):
        self.ledBaseColors[index]=list(bytearray.fromhex(self.colorSchemes[newColorScheme][index]))
  
  def calculateBrightness( self, cycleTime, currentTime, startTime, pulseWidth):
    time = currentTime%cycleTime
    endTime = startTime+pulseWidth

    if(((endTime) < cycleTime) and (time >= startTime) and ((time<=(endTime)%cycleTime))):
      return 0.5 - 0.5 * math.cos((time - startTime) / pulseWidth * 2 * math.pi )
    if((endTime>cycleTime) and ((time >= startTime) or ( time <= endTime%cycleTime))):
      if(time >= startTime):
        return 0.5 - 0.5 * math.cos((time - startTime) / pulseWidth * 2 * math.pi )
      else:
        return 0.5 - 0.5 * math.cos((time+cycleTime - startTime) / pulseWidth * 2 * math.pi )
    else:
      # print(   f'  current:{currentTime}/{time}, start:{startTime}, end:{endTime}, pulseW :{pulseWidth}') 
      return 0
    
  
  def heartbeat(self): 
    timeDelay = .025
    currentTime = 0

    # self.updateColorScheme('nathan')
    # print(self.ledBaseColors)//

    while( True ):
      # print(f'Time: {currentTime}/')
      secPerBeat = 60/self.bpm
      for index, led in enumerate(self.ledConfig):
        brightness = self.calculateBrightness( secPerBeat, currentTime, led['startTime']*secPerBeat, led['pulseWidth']*secPerBeat )
        # print(f'led: {index+1}, brightness: {brightness}')
        if index < 7:
          self.strand2[index]=tuple(round(i * 0.5* brightness) for i in self.ledBaseColors[index])
        else:
          self.strand[index-7]=tuple(round(i *0.5* brightness) for i in self.ledBaseColors[index])
          
        # print(self.strand)
        # print(self.strand2)
      self.strand2.write()
      self.strand.write()
      
      time.sleep(timeDelay)
      
      currentTime += timeDelay