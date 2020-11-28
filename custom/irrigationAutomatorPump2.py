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
chan = AnalogIn(ads, ADS.P1)
relay = OutputDevice(27, active_high=False, initial_value=False)

# Probe calibration parameters
probeWet = 1.180
probeDry = 2.330
probeRange = probeDry - probeWet


# Constants

totalSecondsInDay = 86400.0

wateringCheckInterval = 900 # Check every 15 minutes

pumpToggleThreshold = 0.7

postWaterDelayCheck = 60

maxWaterPumpingPerDayInSeconds = 32
maxWaterPumpingPerActivationInSeconds = 8
maxPumpActivationsPerDay = int(maxWaterPumpingPerDayInSeconds / maxWaterPumpingPerActivationInSeconds)


preWateringMessage = "{0}\tPre Water Probe Reading\t\t--- Moisture voltage: {1:.3f} --- Moisture ratio: {2:.3f} --- Water time: {3} seconds"
postWateringMessage = "{0}\tPost Water Probe Reading\t--- Moisture voltage: {1:.3f} --- Moisture ratio: {2:.3f}"
maxWateringWarning = "{0}\tWARNING: Max watering threshold reached. Unable to water until {1}."
baseReadingMessage = "{0}\tProbe Reading\t--- Moisture voltage: {1:.3f} --- Moisture ratio: {2:.3f}"



# Variables
waterTimingsPump = []



while True:

  # Check oldest entry for potential removal
  if (len(waterTimingsPump) != 0):
    timeNow = datetime.now()
    elapsed = timeNow - waterTimingsPump[0]

    if(elapsed.total_seconds() > totalSecondsInDay):
      waterTimingsPump.pop(0)


  # Check the probe to see if should water
  probeMoistureRatio = (chan.voltage - probeWet) / probeRange

  if (probeMoistureRatio > pumpToggleThreshold):

    # Ensure max watering threshold not exceeded
    if (len(waterTimingsPump) < maxPumpActivationsPerDay):

      # Safe to water
      print(preWateringMessage.format(datetime.now(), chan.voltage, probeMoistureRatio, maxWaterPumpingPerActivationInSeconds))

      waterTimingsPump.append(datetime.now())
      relay.on()
      sleep(maxWaterPumpingPerActivationInSeconds)
      relay.off()
      sleep(postWaterDelayCheck)

      probeMoistureRatio = (chan.voltage - probeWet) / probeRange
      print(postWateringMessage.format(datetime.now(), chan.voltage, probeMoistureRatio))

    else:

      # Unable to water due to max threshold reached.
      timeNow = datetime.now()
      timeNext = waterTimingsPump[0] + timedelta(days=1)

      print(maxWateringWarning.format(timeNow, timeNext))
      print(baseReadingMessage.format(timeNow, chan.voltage, probeMoistureRatio))

  else:

    # Not time to water yet
    print(baseReadingMessage.format(datetime.now(), chan.voltage, probeMoistureRatio))


  # Sleep until next check in timing.
  sleep(wateringCheckInterval)

