import smbus
from models.plant import Plant
from models.sensor import Sensor

from tools.sensor import ToolChainSensor


class TSL2561(object):
  """docstring for TSL2561"""

  def __init__(self):
    super(TSL2561, self).__init__()

  @staticmethod
  def run(busnumber=1, tsl_adress=0x39):
    start = 0x51

    ambiance_lowbyte = 0
    ambiance_highbyte = 0
    ambiance = 0

    ir_lowbyte = 0
    ir_highbyte = 0
    ir = 0

    ratio = 0
    lux = 0

    i2c_bus = smbus.SMBus(busnumber)
    i2c_bus.write_byte_data(tsl_adress, 0x80, 0x03)

    ambiance_lowbyte = i2c_bus.read_byte_data(tsl_adress, 0x8c)
    ambiance_highbyte = i2c_bus.read_byte_data(tsl_adress, 0x8d)
    ambiance = (ambiance_highbyte * 256) + ambiance_lowbyte

    ir_lowbyte = i2c_bus.read_byte_data(tsl_adress, 0x8e)
    ir_highbyte = i2c_bus.read_byte_data(tsl_adress, 0x8f)
    ir = (ir_highbyte * 256) + ir_lowbyte

    if ambiance == 0:
      ratio = 0
    else:
      ratio = ir / float(ambiance)

    # (calulation according to the datasheet)
    if 0 < ratio <= 0.50:
      lux = 0.0304 * ambiance - 0.062 * ambiance * (ratio**1.4)
    elif 0.50 < ratio <= 0.61:
      lux = 0.0224 * ambiance - 0.031 * ir
    elif 0.61 < ratio <= 0.80:
      lux = 0.0128 * ambiance - 0.0153 * ir
    elif 0.80 < ratio <= 1.3:
      lux = 0.00146 * ambiance - 0.00112 * ir
    else:
      lux = 0



    plant = Plant.get(Plant.localhost == True)

    tools = ToolChainSensor()
    light = {'sensor': Sensor.get(Sensor.name == 'light'),
             'plant': plant,
             'value': lux}

    if tools.insert_data(light):
      tools.set_hardware(light)
    print(light)

if __name__ == '__main__':
    TSL2561.run()

# # define TSL specific stuff
# busnumber = 1
# adressTSL2561 = 0x39
# start = 0x51

# # define vars needed for ambiance
# ambianceHighByte = 0
# ambianceLowByte = 0
# ambiance = 0

# # define vars infrared
# IRHighByte = 0
# IRLowByte = 0
# IR = 0

# # define other cool stuff!
# ratio = 0
# lux = 0

# # instanciate I2C
# i2cBus = smbus.SMBus(busnumber)

# # start measureing (400ms)
# i2cBus.write_byte_data(adressTSL2561, 0x80, 0x03)

# # get and calculate stuff...
# # AWESOME!

# # ambient
# ambianceLowByte = i2cBus.read_byte_data(adressTSL2561, 0x8c)
# ambianceHighByte = i2cBus.read_byte_data(adressTSL2561, 0x8d)
# ambiance = (ambianceHighByte*256)+ambianceLowByte

# # infrared
# IRLowByte = i2cBus.read_byte_data(adressTSL2561, 0x8e)
# IRHighByte = i2cBus.read_byte_data(adressTSL2561, 0x8f)
# IR = (IRHighByte*256)+IRLowByte

# # ratio
# if ambiance == 0:
#   ratio = 0
# else:
#   ratio = IR / float (ambiance)

# # now calculations on the very important part!
# # LUX
# # (calulation according to the datasheet)
# if 0 < ratio <= 0.50:
#     lux = 0.0304*ambiance-0.062*ambiance*(ratio**1.4)
# elif 0.50 < ratio <= 0.61:
#     lux = 0.0224*ambiance-0.031*IR
# elif 0.61 < ratio <= 0.80:
#     lux = 0.0128*ambiance-0.0153*IR
# elif 0.80 < ratio <= 1.3:
#     lux = 0.00146*ambiance-0.00112*IR
# else:
#     lux = 0

# # make stuff with data
# toolChain = Tools(db, plantAbbreviation)
# toolChain.insertSensor('l', round(lux, 2))

# mailer = PlantMailer(plantAbbreviation,'l')
# mailer.send()

# generalLight = generalStatus(plantAbbreviation, 'l', round(lux,2))
# generalLight.insert()
# generalLight.set()
