import smbus
import tools.logger
from models.plant import Plant
from models.sensor import Sensor

from tools.sensor import ToolChainSensor


class TSL2561(object):
  """docstring for TSL2561"""

  def __init__(self):
    super(TSL2561, self).__init__()

  @staticmethod
  def run(busnumber=1, tsl_adress=0x39):
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
    i2c_bus.write_byte_data(tsl_adress, 0x81, 0x12)  # 16X gain

    proceeding = False
    pointer = 0
    while not proceeding:
      ambiance_lowbyte = i2c_bus.read_byte_data(tsl_adress, 0x8c)
      ambiance_highbyte = i2c_bus.read_byte_data(tsl_adress, 0x8d)
      ambiance = (ambiance_highbyte * 256) + ambiance_lowbyte

      ir_lowbyte = i2c_bus.read_byte_data(tsl_adress, 0x8e)
      ir_highbyte = i2c_bus.read_byte_data(tsl_adress, 0x8f)
      ir = (ir_highbyte * 256) + ir_lowbyte

      if (ambiance >= 65535 or ir >= 65535) and pointer == 0:
        i2c_bus.write_byte_data(tsl_adress, 0x81, 0x02)  # 1X gain
      else:
        proceeding = True
      pointer += 1

    if pointer > 1:
      ambiance *= 16    # scaling 1X to 16X
      ir *= 16          # scaling 1X to 16X

    if ambiance == 0:
      ratio = 0
    else:
      ratio = ir / float(ambiance)

    # calculations according to the datasheet
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

    plant = Plant.get(localhost=True)

    toolchain = ToolChainSensor()
    light = {'sensor': Sensor.get(name='light'),
             'plant': plant,
             'value': lux}

    if toolchain.insert_data(light):
      toolchain.set_hardware(light)

if __name__ == '__main__':
    TSL2561.run()
