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
    HRMonitor.sensor.set_sample_rate(100)
    
    print( "It's alive!" )
    self.hrRunLoop()

  def configure_max30102(self, i2c):
    # My Code
    pulseAmp = 0x1F
    ledAmp = 0x1F
    self.sensor.set_pulse_amplitude_red(pulseAmp)
    self.sensor.set_pulse_amplitude_it(pulseAmp)
    self.sensor.set_active_leds_amplitude(ledAmp)

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
    
    # self.recentMax = max(self.irRollingAverage)
    # self.recentMin = min(self.irRollingAverage)

    if (self.filteredValuesCount>self.irRollingAverageBufferLen)and (self.irBuffer[1] > self.irBuffer[0] and self.irBuffer[1] > self.irBuffer[2]) and ((self.irBuffer[1] - self.irBuffer[0]) < 20) and ((self.irBuffer[1] - self.irBuffer[2]) < 20): #and ((self.irBuffer[1]-self.recentMin)/(self.recentMax-self.recentMin)> 0.70 )
      return True
    return False
    

  # def calculate_heart_rate(self, ir_data_array, sample_rate=100, ema_alpha=0.2, moving_average_length=3):
  #   peak_values = self.find_peaks(ir_data_array, 750)
  #   if(len(peak_values) >= 2):
  #     time_interval = (peak_values[-1] - peak_values[0])/sample_rate
  #     heart_rate = 60/time_interval
  #     return heart_rate
  #   return None

  def hrRunLoop(self):
    # Check if the Max30102 is present
    self.sensor.check()
    recentPeaks = [utime.ticks_ms()]*3

    time.sleep(2)

    print("Checking Sensor")
    self.sensor.check()
    if( not self.sensor.available() ):
      print("Max30102 not found. Check wiring.")
      return 
    
    # Configure the Max30102
    self.configure_max30102(self.i2cHandle)

    # Using the Pi LED for HR Feedback
    led = Pin(25, Pin.OUT)
    count = 0
    hrBuffer = [0]*3
    heartRate = 0
    while True:
        # Read data from the Max30102
        self.sensor.check()
       
        if( self.sensor.available() ):
            redReading = self.sensor.pop_red_from_storage()
            irReading = self.sensor.pop_ir_from_storage()
            count += 1
            if irReading <= 4000 and irReading >= 2800:
                led.on()
                if count > 10:
                    if(self.oohIsThatAPeak(irReading)):
                      led.off()
                      recentPeaks.append(utime.ticks_ms())
                      recentPeaks.pop(0)

                      #calculate the BPM between each peak, if we have three consistent beats, update the pretty lights...
                      newGap = utime.ticks_diff(recentPeaks[2],recentPeaks[1])

                      heartRate = 60/newGap*1000                      
                      hrBuffer.append(heartRate)
                      hrBuffer.pop(0)

                      print(f"HR:{hrBuffer} updating lights.... ")
                      if(max(hrBuffer) <= min(hrBuffer) * 1.2):        
                        #we have a consitent gap of samples between peaks, lets call it a HR so I can get some sleep...
                        print("Updating LEDs")
                        self.ledHandle.updateBPM( max(min(hrBuffer[-1],200),40))

                    # print(f"{irReading} {self.irBuffer[-1]} {self.recentMin} {self.recentMax} {beat}")                    
            else:
               count = 0
               self.filteredValuesCount = 0
               led.off()

            time.sleep(0.01)
        else:
            time.sleep(0.01)