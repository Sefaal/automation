from gpiozero import OutputDevice
from time import sleep
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import datetime
from datetime import datetime, timedelta


# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
# you can specify an I2C adress instead of the default 0x48
# ads = ADS.ADS1115(i2c, address=0x49)

# Create single-ended input on channel 0
chan1 = AnalogIn(ads, ADS.P0)
chan2 = AnalogIn(ads, ADS.P1)

# Create differential input between channel 0 and 1
# chan = AnalogIn(ads, ADS.P0, ADS.P1)

relay1 = OutputDevice(17, active_high=False, initial_value=False)
relay2 = OutputDevice(27, active_high=False, initial_value=False)

# Probe calibration parameters
probe1wet = 1.135
probe1dry = 2.265
probe1range = probe1dry - probe1wet

probe2wet = 1.180
probe2dry = 2.330
probe2range = probe2dry - probe2wet

#print("probe1range result: {:>5.3f}".format(probe1range))
#print("probe2range result: {:>5.3f}".format(probe2range))


# Constants

totalSecondsInDay = 86400.0

wateringCheckInterval = 3600 #Check every hour

pumpToggleThreshold = 0.7

postWaterDelayCheck = 60

maxWaterPumpingPerDayInSeconds = 32
maxWaterPumpingPerActivationInSeconds = 8
maxPumpActivationsPerDay = int(maxWaterPumpingPerDayInSeconds / maxWaterPumpingPerActivationInSeconds)
#print(maxPumpActivationsPerDay)

preWateringMessage = "{0}\tPre Water Probe Reading\t--- Moisture voltage: {1:.3f} --- Moisture ratio: {2:.3f} --- Watering time: {3} seconds"
postWateringMessage = "{0}\tPost Watering Probe Reading\t--- Moisture voltage: {1:.3f} --- Moisture ratio: {2:.3f}"
maxWateringWarning = "{0}\tWARNING: Max watering threshold reached. Unable to water until {1}."
baseReadingMessage = "{0}\tProbe Reading\t--- Moisture voltage: {1:.3f} --- Moisture ratio: {2:.3f}"






# Variables
waterTimingsPump1 = []
#waterTimingsPump2 = []



#testTime = datetime(2020, 11, 23, 12, 0, 0, 0)
#waterTimingsPump1.append(testTime)
#print(len(waterTimingsPump1))
#print(waterTimingsPump1[0])


#print("P1:\t{:>5}\t{:>5}\t{:>5}\t\tP2:\t{:>5}\t{:>5}\t{:>5}".format("raw", "v", "%", "raw", "v", "%"))

while True:


  # Check oldest entry for potential removal
  if (len(waterTimingsPump1) != 0):
    timeNow = datetime.now()
    elapsed = timeNow - waterTimingsPump1[0]
    #print(elapsed.total_seconds())

    if(elapsed.total_seconds() > totalSecondsInDay):
      #print("Removing {0}".format(waterTimingsPump1[0]))
      waterTimingsPump1.pop(0)



  # Check the probe to see if should water
  probe1MoistureRatio = (chan1.voltage - probe1wet) / probe1range

  if (probe1MoistureRatio > pumpToggleThreshold):

    # Ensure max watering threshold not exceeded
    if (len(waterTimingsPump1) < maxPumpActivationsPerDay):

      # Safe to water
      print(preWateringMessage.format(datetime.now(), chan1.voltage, probe1MoistureRatio, maxWaterPumpingPerActivationInSeconds))

      relay1.on()
      sleep(maxWaterPumptingPerActivationInSeconds)
      relay1.off()
      sleep(postWaterDelayCheck)

      probe1MoistureRatio = (chan1.voltage - probe1wet) / probe1range
      print(postWateringMessage.format(datetime.now(), chan1.voltage, probe1MoistureRatio))

    else:

      # Unable to water due to max threshold reached.
      timeNow = datetime.now()
      timeNext = waterTimingsPump1[0] + timedelta(days=1)

      print(maxWateringWarning.format(timeNow, timeNext))
      print(baseReadingMessage.format(timeNow, chan1.voltage, probe1MoistureRatio))

  else:

    # Not time to water yet
    print(baseReadingMessage.format(datetime.now(), chan1.voltage, probe1MoistureRatio))


  # TODO: Would need to repeat the code above for the 2nd pump relay...


  # Sleep until next check in timing.
  sleep(wateringCheckInterval)



#  probe2MoistureRatio = (chan2.voltage - probe2wet) / probe2range

#  if (probe1MoistureRatio < pumpToggleThreshold):
#    chan1result = "P1-Off:\t{:>5}\t{:>5.3f}\t{:>5.3f}".format(chan1.value, chan1.voltage, probe1MoistureRatio)
#  else:
#    chan1result = "P1-On:\t{:>5}\t{:>5.3f}\t{:>5.3f}".format(chan1.value, chan1.voltage, probe1MoistureRatio)

#  if (probe2MoistureRatio < pumpToggleThreshold):
#    chan2result = "P2-Off:\t{:>5}\t{:>5.3f}\t{:>5.3f}".format(chan2.value, chan2.voltage, probe2MoistureRatio)
#  else:
#    chan2result = "P2-On:\t{:>5}\t{:>5.3f}\t{:>5.3f}".format(chan2.value, chan2.voltage, probe2MoistureRatio)

#  print(chan1result + "\t\t" + chan2result)

