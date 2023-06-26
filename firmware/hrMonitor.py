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
    time.sleep(2) # Wait for Sensor to Come Up - TODO: Be scientific about this delay
    print( "Setting up sensor" )
    HRMonitor.sensor = MAX30102(i2c=self.i2cHandle)
    HRMonitor.sensor.setup_sensor()
    print( "It's alive!" )
    self.hrRunLoop()

  def hrRunLoop(self):
    print("runloop")
    pulseAmp = 0x1F
    ledAmp = 0x1F

    # HR Tuning
    HRMonitor.sensor.set_pulse_amplitude_red(pulseAmp)
    HRMonitor.sensor.set_pulse_amplitude_it(pulseAmp)
    HRMonitor.sensor.set_active_leds_amplitude(ledAmp)

    if( constants.HR_TESTING ):
        lastBeatTime = 0
        arrSize = 5
        timeoutCount = 50
        bpmAvgSize = 10
        arrIndex = 0
        rollingAverageArray = [0] * arrSize
        bpmAvgArray = [0] * bpmAvgSize
        bpmIndex = 0
        bpmAvg = 0.0
        count = timeoutCount
        waitForBeat = True
        sensorActive = False
        
        #time.sleep(5)
        print( "Runloop" )
        while True:        
            HRMonitor.sensor.check()
            
            if( HRMonitor.sensor.available() ):
                now = time.ticks_ms()
                irValue = HRMonitor.sensor.pop_ir_from_storage()
                red_sample = HRMonitor.sensor.pop_red_from_storage()
                
                if( irValue > 2000 or sensorActive ):
                    sensorActive = True
                    avgValue = 0.0
                    rollingAverageArray[arrIndex] = irValue
                    arrIndex = ( arrIndex + 1 ) % arrSize
                    
                    for i in range(5):
                        avgValue = rollingAverageArray[i] + avgValue
                    avgValue = avgValue / 5.0
                    
                    if( ( irValue - avgValue ) < -4 ):
                        count = timeoutCount
                        
                        if( waitForBeat ):
                            print( "beat" )
                            waitForBeat = False                
                            delta = ( now - lastBeatTime ) / 1000.0
                            lastBeatTime = now
                            bpmAvgArray[bpmIndex] = (60.0 / delta)
                            bpmIndex = ( bpmIndex + 1 ) % bpmAvgSize
                            
                            for i in range(bpmAvgSize):
                                bpmAvg = bpmAvgArray[i] + bpmAvg
                            bpmAvg = bpmAvg / float(bpmAvgSize)
                            bpm = int(bpmAvg)
                            print("BPM Value" + str(bpm))
                            if( bpm > 50 and bpm < 200 ):
                              self.ledHandle.updateBPM(bpm)
                    elif( ( irValue - avgValue ) > 1  ):
                        waitForBeat = True
                    else:
                        if( count > 0 ):
                            count = count - 1
                            if( count == 0 ):
                                sensorActive = False
                                lastBeatTime = now
                                bpmAvgArray = [0] * bpmAvgSize
                                bpmIndex = 0
                                bpmAvg = 0.0
                                bpm = 0
                else:
                    # Delay HR measurement to save power when sensor is inactive
                    print( "hr read delay" )
                    time.sleep(3)
                #print(",".join(map(str,[now,irValue,avgValue,irValue-avgValue,bpmAvg])))
