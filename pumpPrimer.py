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


pumpPrimingTime = 30


print("Pump Primer --- Pumps will run for {0} seconds!".format(pumpPrimingTime))

relay1.on()
relay2.on()
sleep(pumpPrimingTime)
relay1.off()
relay2.off()

print("Pump Primer --- Priming complete!")

