import time
import constants
import leds
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

    self.setupSensor()

  def setupSensor(self):
    result = self.i2cHandle.scan()
    time.sleep(0.9) # Wait for Sensor to Come Up - TODO: Be scientific about this delay
    print( "Setting up sensor" )
    HRMonitor.sensor = MAX30102(i2c=self.i2cHandle)
    HRMonitor.sensor.setup_sensor()
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

  def calculate_heart_rate(self, ir_data_array, sample_rate=100, ema_alpha=0.2, moving_average_length=3):
    peak_values = self.find_peaks(ir_data_array, 750)
    if(len(peak_values) >= 2):
       time_interval = (peak_values[-1] - peak_values[0])/sample_rate
       heart_rate = 60/time_interval
       return heart_rate
    return None

  

  def hrRunLoop(self):        
    # Check if the Max30102 is present
    self.sensor.check()

    time.sleep(2)

    print("Checking Sensor")
    self.sensor.check()
    if( not self.sensor.available() ):
        print("Max30102 not found. Check wiring.")
        return 
    
    # Configure the Max30102
    self.configure_max30102(self.i2cHandle)

    ir_data_array = []
    # Variables for BPM filtering
    bpm_ema_alpha = 0.1
    bpm_ema = None
    led = Pin(25, Pin.OUT)
    count = 0
    while True:
        # Read data from the Max30102
        # red_data, ir_data = read_max30102_data(i2c)
        self.sensor.check()
        if( self.sensor.available() ):            
            red_data = self.sensor.pop_red_from_storage()
            ir_data = self.sensor.pop_ir_from_storage()
            
            if ir_data <= 4500 and ir_data >= 3500:
                if count > 100:
                    led.on()
                    filtered = self.filter(ir_data)
                    print(f"{ir_data};{filtered}")
                    ir_data_array.append(filtered)
                else: 
                    count += 1
            else:
               count = 0
               led.off()

            # Limit the size of the array to prevent excessive memory usage
            max_array_size = 100
            if len(ir_data_array) > max_array_size:
                ir_data_array = ir_data_array[-max_array_size:]

            # Calculate heart rate and print it to the console
            heart_rate = self.calculate_heart_rate(ir_data_array)
            if heart_rate is not None and heart_rate > 40 and heart_rate < 200:
                # print("Filtered Heart Rate:", round(heart_rate), "BPM")
                pass
            else:
                print("Heart Rate calculation failed. Not enough peaks detected.")
                pass
            # Wait a moment before taking the next reading
            time.sleep(0.01)
        else:
            time.sleep(0.05)