import time
import utime
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
  
  'zombie':
  ['ffff00','00ff00','ffff00','00ff00','ffff00','00ff00','ffff00',
   '00ff00','ffff00','00ff00','ffff00','00ff00','ffff00','00ff00'],

  'green':
  ['00ff00']*14,

  'red':
  ['ff0000']*14,

  'orange':
  ['ff1500']*14,

  'yellow':
  ['ffff00']*14,

  'blue':
  ['0000ff']*14,

  'purple':
  ['ff00ff']*14,

  'cinnamontoastcrunch': 
  ['ce9958','ce9958','724705','724705','d8d09f','d8d09f','d8d09f',
   'ce9958','b8732d','b8732d','b8732d','9f633b','9f633b','9f633b'],
  
  'fruitypebbles':
  ['f0aa37','ffd52b','00ffd7','2edfb4','10b990','9476d6','f23333', 
   '9476d6','d65a8a','00ffd7','2edfb4','9476d6','f23333','f23333'],
  
  # 'luckycharms':
  # ['216209', '8fac06', 'bdd9a3', '56a20d', '91d521'],
  
  # 'fruitloops':
  # ['ff0000', 'ffe700', '7cff00', 'c900ff', '00dfff'],
  
  # 'trix':
  # ['58e3ff', '87a2ff', 'af7ffc', 'da4e7d', 'f14848'], 
  
  'rainbow':
  ['ff008f', 'ff00ff', '0010ff', '00cfff', '00ff00', 'ff5500', 'ff1500',
   'ff00ff', '0020ff', '00cfff', '00ff00', 'ffaf00', 'ff1500','ff0000',],

  'applejacks':
  ['3cbf2e', 'e88f23', '7a4606', '3cbf2e', 'e88f23', '7a4606', '3cbf2e', 
   'e88f23', '7a4606', '3cbf2e', 'e88f23', '7a4606', '3cbf2e', 'e88f23']

  #  'booberry':
  #  ['8362a6','68bce3','4a7e96','fc0505'],

  #   'creepercrunch':
  #  ['8fe38f','0f800f','0db50d','609e60','004500'],

  #  'reesespuffs':
  #  ['fe5200','551e0a','fdef14'],

  #  'carmellacreeper':
  #  ['22b32c','a2b322','e56fed','ed6fb7'],

  #  'frankenberry':
  #  ['ed6fb7','6fc1ed','cf84f0','e5dfe8']
}

  startupConfig = [ \
    {'startTime': 0.3237, 'pulseWidth': 0.50}, #1
    {'startTime': 0.2016, 'pulseWidth': 0.50}, #2
    {'startTime': 0.0873, 'pulseWidth': 0.50}, #3
    {'startTime': 0.0972, 'pulseWidth': 0.50}, #4
    {'startTime': 0.0760, 'pulseWidth': 0.50}, #5
    {'startTime': 0.2154, 'pulseWidth': 0.50}, #6
    {'startTime': 0.2739, 'pulseWidth': 0.50}, #7
    {'startTime': 0.1781, 'pulseWidth': 0.50}, #8
    {'startTime': 0.1110, 'pulseWidth': 0.50}, #9
    {'startTime': 0.1004, 'pulseWidth': 0.50}, #10
    {'startTime': 0.0967, 'pulseWidth': 0.50}, #11
    {'startTime': 0.2241, 'pulseWidth': 0.50}, #12
    {'startTime': 0.3065, 'pulseWidth': 0.50}, #13
    {'startTime': 0.3417,	'pulseWidth': 0.50}] #14
  
  ledConfig = [ \
    {'startTime': 0.6484, 'pulseWidth': 0.5508}, #1
    {'startTime': 0.6712, 'pulseWidth': 0.7581}, #2
    {'startTime': 0.1585, 'pulseWidth': 0.4541}, #3
    {'startTime': 0.2585, 'pulseWidth': 0.3041}, #4
    {'startTime': 0.4508, 'pulseWidth': 0.445}, #5
    {'startTime': 0.5223, 'pulseWidth': 0.4670}, #6
    {'startTime': 0.6000, 'pulseWidth': 0.3256}, #7
    {'startTime': 0.6712, 'pulseWidth': 0.7581}, #8
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
    # ledControl = Pin( 25, Pin.OUT)
    self.ledPower = Pin( 22, Pin.OUT)
    self.ledPower.on()
    self.strand = NeoPixel(ledDataPin, 7) #[0]*7 
    #
    self.strand2 = NeoPixel(deoxPin, 7) # [0]*7
    self.bpm = 60
    self.newBPM = 0
    self.offset = 0
    self.colorScheme = "heart"
    self.ledBaseColors = [[0]*3]*14
    self.secPerBeat = 1000

    self.updateColorScheme(self.colorScheme)
  
  def shutdown(self):
    for led in range(7): 
      self.strand[led] = tuple([0,0,0])
      self.strand2[led] = tuple([0,0,0])
    self.strand.write()      
    self.strand2.write()
    self.ledPower.off()
    return True   

  def wakeup(self):
    self.ledPower.on()

  def updateBPM( self, newBPM ):
    self.newBPM = newBPM

  def updateColorScheme( self, newColorScheme ):
    print( f'Changing color to: {newColorScheme}')
        
    #sets up a base color list/array thats easier to work with from the generic hex values that are easier to edit.  Done only on change for efficiency...
    if newColorScheme in self.colorSchemes:
      self.colorScheme = newColorScheme
      for index, color in enumerate(self.colorSchemes[newColorScheme]):
        self.ledBaseColors[index]=list(bytearray.fromhex(self.colorSchemes[newColorScheme][index]))
    else:
      print("Could not Find Color")
  
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
    

  def startupWave(self):

    startTime = utime.ticks_ms()
    currentTime = startTime
    self.secPerBeat = 2000
    self.offset = self.secPerBeat-currentTime%self.secPerBeat # special sauce to still use the general tick_ms time, but ensure we start at 0.
  
    while( currentTime < (startTime+self.secPerBeat )):

      currentTime = utime.ticks_ms()
     
      for index, led in enumerate(self.startupConfig):
        brightness = self.calculateBrightness( self.secPerBeat, currentTime+self.offset, led['startTime']*self.secPerBeat, led['pulseWidth']*self.secPerBeat )
        # print(f'time: {((currentTime+self.offset)%self.secPerBeat)}led: {index+1}, brightness: {brightness}')
        if index < 7:
          self.strand2[index]=tuple(round(i * 0.5* brightness) for i in self.ledBaseColors[index])
        else:
          self.strand[index-7]=tuple(round(i *0.5* brightness) for i in self.ledBaseColors[index])
          
      self.strand2.write()
      self.strand.write()
      
      time.sleep(.025)
      
  def tickHeartbeat(self):
    currentTime = utime.ticks_ms()
    self.secPerBeat = 60000/self.bpm
    if(self.newBPM != 0 ): 
      #need to get smooth transitions,  as a shortcut going to add an offset to place the currentTime next in the same place relative to the cycle. 
      self.offset = ((currentTime+self.offset)%self.secPerBeat)*self.bpm/self.newBPM - currentTime
      self.bpm = self.newBPM
      self.secPerBeat = 60000/self.bpm
      self.newBPM = 0

    for index, led in enumerate(self.ledConfig):
      brightness = self.calculateBrightness( self.secPerBeat, currentTime+self.offset, led['startTime']*self.secPerBeat, led['pulseWidth']*self.secPerBeat )
      # print(f'led: {index+1}, brightness: {brightness}')
      if index < 7:
        self.strand2[index]=tuple(round(i * 0.5* brightness) for i in self.ledBaseColors[index])
      else:
        self.strand[index-7]=tuple(round(i *0.5* brightness) for i in self.ledBaseColors[index])
        
    self.strand2.write()
    self.strand.write()


  def heartbeatRunLoop(self): 
    timeDelay = .025
    while( True ):
      self.tickHeartbeat()  
      time.sleep(timeDelay)