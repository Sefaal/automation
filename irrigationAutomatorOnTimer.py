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

# Create differential input between channel 0 and 1
# chan = AnalogIn(ads, ADS.P0, ADS.P1)

relay1 = OutputDevice(17, active_high=False, initial_value=False)
relay2 = OutputDevice(27, active_high=False, initial_value=False)


# Constants
initialDelay = 14400              # Initial delay prior to core program start (in seconds)
activePumpTiming1 = 80            # Pump active time, lasts xx seconds
activePumpTiming2 = 50            # Pump active time, lasts xx seconds
waitForNextPumpTiming = 14400.0   # Pump interval, every 4 hours (in seconds)

# Messages
initialMessage =    "{0}\tWatering program will start in {1:.2f} hours."
wateringMessage =   "{0}\tWatering for {1} seconds on pump {2}."
postWaterMessage =  "{0}\tWatering complete, next watering in {1:.2f} hours."


if (initialDelay > 0):
  print(initialMessage.format(datetime.now(), initialDelay/3600.0))
  sleep(initialDelay)

while True:

  relay1.on()
  print(wateringMessage.format(datetime.now(), activePumpTiming1, 1))
  sleep(activePumpTiming1)
  relay1.off()

  relay2.on()
  print(wateringMessage.format(datetime.now(), activePumpTiming2, 2))
  sleep(activePumpTiming2)
  relay2.off()

  print(postWaterMessage.format(datetime.now(), (waitForNextPumpTiming/3600.0)))
  sleep(waitForNextPumpTiming - (activePumpTiming1 + activePumpTiming2))

