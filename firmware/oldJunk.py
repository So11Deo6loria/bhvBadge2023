## OLD LED STuff
  def heartbeat( neoPixel ):
      global timeDelay
      while( True ):
          if( self.ledState == 'heartbeat' ):
              # The big show
              if( bpm > 50 and bpm < 200 ):
                  timeDelay = (1/(bpm/60))
                  debugPrint(timeDelay)
              while( True ):
                  for i in range(9):
                      for j in range(8):
                          neoPixel[j] = (0,0,0)
                      neoPixel.write()
                      if( i < 8 ):
                          neoPixel[i] = (constants.LED_INTENSITY, 0, 0)
                          neoPixel.write()
                          time.sleep(blinkDelay)
                  time.sleep(1/(bpm/60))
          elif( self.ledState == 'deadbeat' ):
              # Trobbing
              time.sleep(trobDelay)
              for intensity in range(0, 128, 1):
                  for led in range(8):
                      neoPixel[led] = (intensity, 0, 0)
                      blueNeopixel[led] = (0, 0, intensity)
                  neoPixel.write()
                  blueNeopixel.write()
                  time.sleep(trobRate)
  #            time.sleep(0.25)
              for intensity in range(0, 128, 1):
                  for led in range(8):
                      neoPixel[led] = (127 - intensity, 0, 0)
                      blueNeopixel[led] = (0, 0, 127 - intensity)
                  neoPixel.write()
                  blueNeopixel.write()
                  time.sleep(trobRate)
          elif( self.ledState == 'waveform' ):
              if( bpm > 50 and bpm < 200 ):
                  timeDelay = (1/(bpm/60))
                  debugPrint(timeDelay)
                  
              # TODO:
              intensity = 255
              lowIntensity = round( intensity * 0.05 )
              midIntensity = round( intensity * 0.25  )
              
              # Start Sequence - Hardcoding This Becasue It's Easier and is based on granularity not LEDs which shouldn't change
              for i in range(2):
                  intensityArray = [0] * 8
                  
                  if( i == 0 ):
                      intensityArray[0] = lowIntensity
                  elif( i == 1 ):
                      intensityArray[0] = midIntensity
                      intensityArray[1] = lowIntensity
                      
                  for led in range(len(intensityArray)):
                      neoPixel[led] = (intensityArray[led], 0, 0) # Use an array to drive the intensity
                  neoPixel.write()
                  time.sleep(blinkDelay)
              
              # LED Iteration
              for activeLed in range(8):
                  intensityArray = [0] * 8
                  
                  if( activeLed > 1 ):
                      intensityArray[activeLed-2] = lowIntensity
                  if( activeLed > 0): 
                      intensityArray[activeLed-1] = midIntensity
                  intensityArray[activeLed] = intensity
                  if( activeLed < 7 ):
                      intensityArray[activeLed+1] = midIntensity
                  if( activeLed < 6 ):
                      intensityArray[activeLed+2] = lowIntensity
                  
                  #print( activeLed, repr(intensityArray) )
                  for led in range(8):
                      neoPixel[led] = (intensityArray[led], 0, 0)
                  neoPixel.write()
                  time.sleep(blinkDelay)
                  
              # End Sequence - Hardcoding This Becasue It's Easier and is based on granularity not LEDs which shouldn't change
              for i in range(3):
                  intensityArray = [0] * 8
                  
                  if( i == 0 ):
                      intensityArray[6] = lowIntensity
                      intensityArray[7] = midIntensity
                  elif( i == 1 ):
                      intensityArray[7] = lowIntensity
                      
                  for led in range(len(intensityArray)):
                      neoPixel[led] = (intensityArray[led], 0, 0) # Use an array to drive the intensity
                  neoPixel.write()
                  time.sleep(blinkDelay)
              
              time.sleep(timeDelay)
                  
          elif( self.ledState == 'error' ):
              # Idk some blinky thing maybe some sick error codes
              for led in range(8):
                  neoPixel[led] = (255, 0, 0)
              neoPixel.write()
              time.sleep(0.5)
              for led in range(8):
                  neoPixel[led] = (0, 0, 0)
              neoPixel.write()
              time.sleep(errorDelay)









# Ported this from C code from the following sites: 
# https:#lastminuteengineers.com/max30102-pulse-oximeter-heart-rate-sensor-arduino-tutorial/
# https:#github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library

RATE_SIZE = 4 # Increase this for more averaging. 4 is good.
rates = [0.0] * RATE_SIZE # Array of heart rates
rateSpot = 0
lastBeat = 0 # Time at which the last beat occurred

beatsPerMinute = 0.0
beatAvg = 0.0

# heartRate Constants
#global offset
#offset = 0
IR_AC_Max = 20
IR_AC_Min = -20
IR_AC_Signal_Current = 0
IR_AC_Signal_Previous = 0
IR_AC_Signal_min = 0
IR_AC_Signal_max = 0
IR_Average_Estimated = 0
positiveEdge = 0
negativeEdge = 0
ir_avg_reg = 0
cbuf = [0] * 32
FIRCoeffs = [172, 321, 579, 927, 1360, 1858, 2390, 2916, 3391, 3768, 4012, 4096]

# Average DC Estimator
def averageDCEstimator(avg_reg, x):
  global ir_avg_reg
  
  avg_reg += (((x << 15) - avg_reg) >> 4)
  ir_avg_reg = avg_reg
  return (avg_reg >> 15)

#  Low Pass FIR Filter
def lowPassFIRFilter(din):
    global offset

    cbuf[offset] = din
    
    z = FIRCoeffs[11] * cbuf[(offset - 11) & 0x1F]
    
    for i in range(11):
      z = z + FIRCoeffs[i] * cbuf[(offset - i) & 0x1F] + cbuf[(offset - 22 + i) & 0x1F]
      
    offset = offset + 1
    offset = offset % 32 #Wrap condition
    
    return(z >> 15);

def checkForBeat( sample ):
  global IR_AC_Signal_Current
  global IR_AC_Signal_Previous
  global IR_AC_Max
  global IR_AC_Min
  global IR_AC_Signal_min
  global IR_AC_Signal_max
  global IR_Average_Estimated
  global positiveEdge
  global negativeEdge
  global ir_avg_reg  
  
  beatDetected = False
  
  #  Save current state
  IR_AC_Signal_Previous = IR_AC_Signal_Current
  
  # This is good to view for debugging
  #debugPrint("Signal_Current: ")
  #debugPrint(IR_AC_Signal_Current)

  # Process next data sample
  IR_Average_Estimated = averageDCEstimator(ir_avg_reg, sample)
  IR_AC_Signal_Current = lowPassFIRFilter(sample - IR_Average_Estimated)
  
  debugPrint("IR_AC_Signal_Previous: " + str(IR_AC_Signal_Previous))
  debugPrint("IR_AC_Signal_Current: " + str(IR_AC_Signal_Current))

  #  Detect positive zero crossing (rising edge)
  if ((IR_AC_Signal_Previous < 0) & (IR_AC_Signal_Current >= 0)):
    #Adjust our AC max and min
    IR_AC_Max = IR_AC_Signal_max 
    IR_AC_Min = IR_AC_Signal_min

    positiveEdge = 1
    negativeEdge = 0
    IR_AC_Signal_max = 0

    debugPrint("IR_AC_Max: " + str(IR_AC_Max))
    debugPrint("IR_AC_Min: " + str(IR_AC_Min))
    #print("IR_AC_Max - IR_AC_Min: " + str(IR_AC_Max - IR_AC_Min))
    
    if ((IR_AC_Max - IR_AC_Min) > 20 and (IR_AC_Max - IR_AC_Min) < 1000):
      debugPrint("HeartBeat!!!")
      beatDetected = True

  #  Detect negative zero crossing (falling edge)
  if ((IR_AC_Signal_Previous > 0) & (IR_AC_Signal_Current <= 0)):
    positiveEdge = 0
    negativeEdge = 1
    IR_AC_Signal_min = 0

  #  Find Maximum value in positive cycle
  if (positiveEdge & (IR_AC_Signal_Current > IR_AC_Signal_Previous)):
    IR_AC_Signal_max = IR_AC_Signal_Current

  #  Find Minimum value in negative cycle
  if (negativeEdge & (IR_AC_Signal_Current < IR_AC_Signal_Previous)):
    IR_AC_Signal_min = IR_AC_Signal_Current
  
  return(beatDetected);


def amilli():
    return time.ticks_ms()
 
lastBeat = 0
lastDeadbeat = 0
deadbeatTimeout = 5
while True:
  sensor.check()

  if( sensor.available() ):
      irValue = sensor.pop_ir_from_storage()
      red_sample = sensor.pop_red_from_storage()
    
      now = amilli()
      if ( checkForBeat(irValue) ):
        # We sensed a beat!
        debugPrint("time:" + repr(now))        
        debugPrint("lastBeat:" + repr(lastBeat))
        debugPrint("delta:" + repr(now-lastBeat))
        delta = now - lastBeat;
        debugPrint("Delta: " + repr(delta))
        lastBeat = now
        lastDeadbeat = now # Prevent the timer from expiring immediately when there isn't a beat

        beatsPerMinute = 60.0 / (delta / 1000.0);

        if (beatsPerMinute < 255 and beatsPerMinute > 20):
          rates[rateSpot] = beatsPerMinute # Store this reading in the array
          rateSpot = rateSpot + 1      
          rateSpot = rateSpot % RATE_SIZE # Wrap variable

          # Take average of readings
          beatAvg = 0.0
          for x in range(RATE_SIZE):
            beatAvg = beatAvg + rates[x]
          beatAvg = round((beatAvg / RATE_SIZE), 0)
          bpm = beatAvg
          ledState = 'waveform'
          
        print(",".join(map(str,[now,irValue,beatsPerMinute,beatAvg])))
      print(",".join(map(str,[now,irValue,beatsPerMinute,beatAvg])))                          

