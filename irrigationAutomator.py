from gpiozero import OutputDevice
from time import sleep
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

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

pumpToggleRatio = 0.7

#print("probe1range result: {:>5.3f}".format(probe1range))
#print("probe2range result: {:>5.3f}".format(probe2range))


print("P1:\t{:>5}\t{:>5}\t{:>5}\t\tP2:\t{:>5}\t{:>5}\t{:>5}".format("raw", "v", "%", "raw", "v", "%"))

while True:
  sleep(1)

  probe1MoistureRatio = (chan1.voltage - probe1wet) / probe1range
  probe2MoistureRatio = (chan2.voltage - probe2wet) / probe2range

  if (probe1MoistureRatio < pumpToggleRatio):
    chan1result = "P1-Off:\t{:>5}\t{:>5.3f}\t{:>5.3f}".format(chan1.value, chan1.voltage, probe1MoistureRatio)
    relay1.off()
  else:
    chan1result = "P1-On:\t{:>5}\t{:>5.3f}\t{:>5.3f}".format(chan1.value, chan1.voltage, probe1MoistureRatio)
    relay1.on()

  if (probe2MoistureRatio < pumpToggleRatio):
    chan2result = "P2-Off:\t{:>5}\t{:>5.3f}\t{:>5.3f}".format(chan2.value, chan2.voltage, probe2MoistureRatio)
    relay2.off()
  else:
    chan2result = "P2-On:\t{:>5}\t{:>5.3f}\t{:>5.3f}".format(chan2.value, chan2.voltage, probe2MoistureRatio)
    relay2.on()

  print(chan1result + "\t\t" + chan2result)

