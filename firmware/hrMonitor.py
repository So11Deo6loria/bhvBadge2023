import time
import utime
from max30102 import MAX30102
from machine import Pin

class HRMonitor:
  sensor = None

  def __init__(self, i2cHandle, ledHandle):
    self.i2cHandle = i2cHandle
    self.ledHandle = ledHandle
    self.b0 = 0.7
    self.b1 = 0.7
    self.a1 = 0.35
    self.x_prev = 3200
    self.y_prev = 3200
    self.irRollingAverageBufferLen = 30
    self.filteredValuesCount = 0
    self.irRollingAvgPeakBufferLen = 5
    self.irRollingAverage = [0]*self.irRollingAverageBufferLen
    self.irBuffer = [0]*3
    self.recentMax=0
    self.recentMin=0
  
    self.setupSensor()

  def setupSensor(self):
    result = self.i2cHandle.scan()
    time.sleep(0.9) # Wait for Sensor to Come Up - TODO: Be scientific about this delay
    print( "Setting up sensor" )
    HRMonitor.sensor = MAX30102(i2c=self.i2cHandle)
    HRMonitor.sensor.setup_sensor()
    HRMonitor.sensor.set_sample_rate(200)
    
    print( "It's alive!" )
    self.sensor.check()

  def filter(self, x_curr):
    y_curr = self.b0*x_curr + self.b1*self.x_prev - self.a1*self.y_prev
    self.x_prev = x_curr
    self.y_prev = y_curr
    return y_curr

  def find_peaks(self, ir_data, threshold):
    peaks = []

    for i in range(1, len(ir_data)-1):
        if ir_data[i] > ir_data[i-1] and ir_data[i] > ir_data[i+1] and ir_data[i] > threshold:
          peaks.append(i)
    return peaks

  def oohIsThatAPeak( self, ir_data ):

    self.filteredValue = self.filter(ir_data)
    self.irRollingAverage.append(ir_data)
    self.irRollingAverage.pop(0)
    self.irBuffer.append(sum(self.irRollingAverage[-self.irRollingAvgPeakBufferLen:])/self.irRollingAvgPeakBufferLen) 
    self.irBuffer.pop(0)
    self.filteredValuesCount += 1
    
    if (self.filteredValuesCount>self.irRollingAverageBufferLen)and (self.irBuffer[1] > self.irBuffer[0] and self.irBuffer[1] > self.irBuffer[2]) and ((self.irBuffer[1] - self.irBuffer[0]) < 20) and ((self.irBuffer[1] - self.irBuffer[2]) < 20): #and ((self.irBuffer[1]-self.recentMin)/(self.recentMax-self.recentMin)> 0.70 )
      return True
    return False
    
  def shutdown(self):
    self.sensor.shutdown()
    self.picoLED.off()
  
  def wakeUp(self):
     self.sensor.wakeup()
  def configureHRSensor(self):


    print("Checking Sensor")
    self.sensor.check()
    if( not self.sensor.available() ):
      print("Max30102 not found. Check wiring.")
      return 
    
    # Configure the Max30102
    pulseAmp = 0x1F
    ledAmp = 0x1F
    self.sensor.set_pulse_amplitude_red(pulseAmp)
    self.sensor.set_pulse_amplitude_it(pulseAmp)
    self.sensor.set_active_leds_amplitude(ledAmp)

    # Using the Pi LED for HR Feedback
    self.picoLED = Pin(25, Pin.OUT)
    self.rawReadingCount = 0
    self.recentPeaks = [utime.ticks_ms()]*3
    self.bpmReadings = [0]*3
    
    
  def hrRunLoop(self):
    # self.configureHRSensor()

    # while True:
        # Read data from the Max30102
        if( self.sensor.safe_check(10) ):
            # redReading = self.sensor.pop_red_from_storage()
            irReading = self.sensor.pop_ir_from_storage()
        
            self.rawReadingCount += 1
            # print(irReading)
            if irReading <= 4000 and irReading >= 2800:
                self.picoLED.on()
                if self.rawReadingCount > 10:
                    if(self.oohIsThatAPeak(irReading)):
                      self.picoLED.off()
                      self.recentPeaks.append(utime.ticks_ms())
                      self.recentPeaks.pop(0)

                      #calculate the BPM between each peak, if we have three consistent beats, update the pretty lights...
                      newGap = utime.ticks_diff(self.recentPeaks[2],self.recentPeaks[1])

                      self.bpmReadings.append(60000/newGap)
                      self.bpmReadings.pop(0)

                      # print(f"HR:{self.bpmReadings}")
                      if(max(self.bpmReadings) <= min(self.bpmReadings) * 1.2):        
                        #we have a consitent gap of samples between peaks, lets call it a HR so I can get some sleep...
                        self.ledHandle.updateBPM( max(min(self.bpmReadings[-1],200),40))
                    
                    # print(f"{irReading} {self.irBuffer[-1]} {self.recentMin} {self.recentMax}")                    
            else:
               self.rawReadingCount = 0
               self.filteredValuesCount = 0
               self.picoLED.off()
        # else:
        #   print('no readings')