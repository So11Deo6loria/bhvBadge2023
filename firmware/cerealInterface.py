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
                   
\" Badges of sky and cell,
 Hold truths, hidden very well.
 Seek, break both the spell. \"

 """

instructions = """

To connect to with your heart, you should start with meditation...  to connect with this badge, thats a different story...

1. Install rshell: Open your terminal or command prompt and run:

  pip install rshell

2. Connect the Board: Plug your board into the computer via USB.

3. Start rshell: Run the following command, replacing /dev/ttyUSB0 with your board's port:

  rshell -p /dev/ttyUSB0

  ...(Most of the time you can just type "rshell")

4. Access the Board's Filesystem: You can now use commands like ls, cp, and edit to interact with the board's filesystem.

  cd /pyboard/path/to/config

5. Edit the File: Use the edit command to modify config.json:
  
  edit config.json

6. Configure the Parameters: Modify the JSON attributes as needed:

  "startupColor": The color pattern that you want to use with the board turns on.
  "heartbeatColor": The color pattern that you want to use when the heart beats. 
  "sleepTimeout": How long do you want the heart to stay on before going to sleep in secconds?

Color Options:  heart, rainbow, green, red, orange, yellow, blue, purple, cinnamontoastcrunch, fruitypebbles, applejacks. 
  
7. Reboot board

  Remove power and reconnect,  Alternatively after saving the file, you can reboot the board by typing "REPL" and using control+D

8. Look Cool

  I mean you've already pretty cool. Enjoy your Defcon. 
"""

def uartVersion(uart):
  uart.write("\r\nSoftware version 1.0\n")

def uartSecret(uart):
  uart.write("\r\nMy Hearts Beats for You!\r\n")

def uartWhoami(uart):
    #just a joke
    uart.write("\r\nheart\r\n")

def uartInstructions(uart):
 
  uart.write(instructions)

def uartPrompt(uart):
  prompt="\r\n> "
  uart.write(prompt)
   

def uartHelp(uart):
  uart.write("\r\nAvailable Commands: \r\n")
  uart.write(" help:    Displays this help window\r\n")
  uart.write(" version: Displays software version number\r\n")
  uart.write(" whoami:  your name\r\n")
  uart.write(" secret:  wanna know a secret...\r\n")
  uart.write(" connect: Instructions to customize me!\r\n")



      
class CerealInterface:
  def __init__(self):
    print("Cereal Init")
    self.uart = UART(0, baudrate=constants.BAUD_RATE, tx=machine.Pin(constants.CEREAL_TX_PIN), rx=machine.Pin(constants.CEREAL_RX_PIN))


  #Run your serial connection with local echo
  def uartShell(self):
    print(self.uart) #for debugging/uart info
    
    prompt="\n> "
    self.uart.write(logo)
    self.uart.write(prompt)

    command = [] # start with blank string
    #Run Shell
    while True:
        # try:
          if self.uart.any():
              data = self.uart.read() #read data from self.uart
              if data == b'\n': #enter recieved 
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
                  elif commandString == "urbreakingmyheart":
                      uartSecret(self.uart)                    
                  elif commandString == "connect":
                      uartInstructions(self.uart)                    
                  elif commandString == "":
                    self.uart.write(prompt)
                  else:
                      self.uart.write("\r\ncmd not recognized try again ")
                      self.uart.write(prompt)

              elif (data == b'\x7f'): # backspace
                  self.uart.write(data)
                  if len(command) > 0:
                    command.pop()
              else:
                  data = data.decode('utf-8') #convert data to string
                  self.uart.write(data)
                  command.append(data)# add value
        # except Exception as e:
          # print("An error occurred:", str(e))
        