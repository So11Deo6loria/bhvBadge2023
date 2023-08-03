import time
import constants
import leds
from max30102 import MAX30102

class HRMonitor:
  sensor = None

  def __init__(self, i2cHandle, ledHandle):
    self.i2cHandle = i2cHandle
    self.ledHandle = ledHandle
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

  def calculate_heart_rate(self, ir_data_array, sample_rate=100, ema_alpha=0.2, moving_average_length=5):
    # Check if the input data is sufficient for moving average filtering
    if len(ir_data_array) < moving_average_length:
        return None

    # Apply a simple moving average filter to the raw IR data
    ir_smoothed = []
    for i in range(len(ir_data_array) - moving_average_length + 1):
        ir_average = sum(ir_data_array[i:i + moving_average_length]) / moving_average_length
        ir_smoothed.append(ir_average)

    # Apply an exponential moving average (EMA) filter to the smoothed IR data
    ema = ir_smoothed[0]
    filtered_ir_data = [ema]
    for ir_data in ir_smoothed[1:]:
        ema = ema_alpha * ir_data + (1 - ema_alpha) * ema
        filtered_ir_data.append(ema)

    # Find peaks (local maxima) in the filtered IR signal
    peaks = []
    for i in range(1, len(filtered_ir_data) - 1):
        if filtered_ir_data[i] > filtered_ir_data[i - 1] and filtered_ir_data[i] > filtered_ir_data[i + 1]:
            peaks.append(i)

    # Calculate time between consecutive peaks and estimate heart rate in BPM
    if len(peaks) >= 2:
        time_between_peaks = (peaks[-1] - peaks[0]) / sample_rate  # Time in seconds between first and last peak
        heart_rate_bpm = 60 / time_between_peaks

        # Range check for BPM values
        min_bpm = 40
        max_bpm = 200
        if min_bpm <= heart_rate_bpm <= max_bpm:
            return heart_rate_bpm
        else:
            return None
    else:
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
    
    while True:
        # Read data from the Max30102
        #red_data, ir_data = read_max30102_data(i2c)
        self.sensor.check()
        if( self.sensor.available() ):            
            red_data = self.sensor.pop_red_from_storage()
            ir_data = self.sensor.pop_ir_from_storage()
            ir_data_array.append(ir_data)

            # Limit the size of the array to prevent excessive memory usage
            max_array_size = 100
            if len(ir_data_array) > max_array_size:
                ir_data_array = ir_data_array[-max_array_size:]

            # Calculate heart rate and print it to the console
            heart_rate = self.calculate_heart_rate(ir_data_array)
            if heart_rate is not None:
                if bpm_ema is None:
                    bpm_ema = heart_rate
                else:
                    bpm_ema = bpm_ema_alpha * heart_rate + (1 - bpm_ema_alpha) * bpm_ema
                print("Filtered Heart Rate:", bpm_ema, "BPM")
            else:
                print("Heart Rate calculation failed. Not enough peaks detected.")

            # Wait a moment before taking the next reading
            time.sleep(0.1)
        else:
            time.sleep(0.05)