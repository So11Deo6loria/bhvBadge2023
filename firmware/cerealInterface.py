import time
import constants
from neopixel import NeoPixel
import machine
from machine import UART


logo = """
 

                 ,*******,                             .*****,                  
                     ,*******                       *******                     
             .     *****  *****                    ******                       
            **  ,****     ,*****                  ********       .**,           
            *******     ****.***                  **********, .*****            
             ****    ,****   ****                *******************            
              ,********      ****              *******************              
                 .********   ***,  ******** *************,...                   
                             ***       ,*************                           
                             ***       ,*** *******                             
                             ****    ***.    *****                              
                             ,***,.***    ,*** ,***                             
                              ,*****    ***     ****                         
                              ***********       ,***                            
                           ,*************,      ****                            
                   ....,************  ********  ****  *********.                
               *******************              ****    .*********.             
             ******************,                ****  /***.    .****            
            ******  **********.                 ,*******     ****.***           
            ***        *******                   ****.    .***     **           
                       *******                    ****, ****       ,            
                     ,******                        ******                      
                   ******                              *******                  

"""

def uartVersion(uart):
  uart.write("Software version ####\r\n")

def uartSecret(uart):
  uart.write("secret: urbreakingmyheart\r\n")
def uartWhoami(uart):
    #just a joke
    uart.write("heart\r\n")

def uartPrompt(uart):
  prompt="\r\n> "
  uart.write(prompt)
   

def uartHelp(uart):
  uart.write("\r\nAvailable Commands: \r\n")
  uart.write(" help:    Displays this help window\r\n")
  uart.write(" version: Displays software version number\r\n")
  uart.write(" whoami:  your name\r\n")
  uart.write(" secret:  ...\r\n")
      
class CerealInterface:
  def __init__(self, pin1, pin2):
    print("Cereal Init")
    self.pin1 = NeoPixel( pin1, 8 )
    self.pin2 = NeoPixel( pin2, 8 )
    

  #Run your serial connection with local echo
  def uartShell(self):
    uart = UART(0, baudrate=constants.BAUD_RATE, tx=machine.Pin(constants.CEREAL_TX_PIN), rx=machine.Pin(constants.CEREAL_RX_PIN))
    print(uart) #for debugging/uart info
    
    uart.write(logo)
    uartPrompt(uart)

    command = [] # start with blank string
    #Run Shell
    while True:
        if uart.any():
            data = uart.read() #read data from uart
            if data == b'\r': #enter recieved 
                commandString = ''.join(command)
                command = []
                print("cmd recieved: "+commandString)
                if commandString == "help":
                    uartHelp(uart)
                elif commandString == "version":
                    uartVersion(uart)
                elif commandString == "whoami":
                    uartWhoami(uart)
                elif commandString == "secret":
                    uartSecret(uart)                    
                elif commandString == "":
                   uart.write(prompt)
                else:
                    uart.write("cmd not recognized try again \r\n")
                    uart.write(prompt)
            elif (data == b'\x7f'): # backspace
                uart.write(data)
                if len(command) > 0:
                  command.pop()
            else:
                data = data.decode('utf-8') #convert data to string
                uart.write(data)
                command.append(data)# add value



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