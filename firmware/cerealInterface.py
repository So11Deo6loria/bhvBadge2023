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


def uartHelp(uart):
  uart.write("help: displays this help window\r\n")
  uart.write("version: displays software version number\r\n")
  uart.write("whoami: your name\r\n")
  uart.write("secret: ...\r\n")
      
class CerealInterface:
  def __init__(self):
    print("Cereal Init")
    self.uart = UART(0, baudrate=constants.BAUD_RATE, tx=machine.Pin(constants.CEREAL_TX_PIN), rx=machine.Pin(constants.CEREAL_RX_PIN))


  #Run your serial connection with local echo
  def uartShell(self):
    print(self.uart) #for debugging/uart info
    
    prompt="Enter your command: "
    self.uart.write(logo)
    self.uart.write(prompt)
    command = [] # start with blank string
    #Run Shell
    while True:
        if self.uart.any():
            data = self.uart.read() #read data from self.uart
            if data == b'\r': #enter recieved 
                commandString = ''.join(command)
                command = []
                print("cmd recieved: "+commandString)
                if commandString == "help":
                    uartHelp(self.uart)
                elif commandString == "version":
                    uartVersion(self.uart)
                elif commandString == "whoami":
                    uartWhoami(self.uart)
                elif commandString == "secret":
                    uartSecret(self.uart)                    
                elif commandString == "":
                   self.uart.write(prompt)
                else:
                    self.uart.write("cmd not recognized try again ")
                    self.uart.write(prompt)
            elif (data == b'\x7f'): # backspace
                if len(command) > 0:
                  command.pop()
            else:
                data = data.decode('utf-8') #convert data to string
                command.append(data)# add value

  