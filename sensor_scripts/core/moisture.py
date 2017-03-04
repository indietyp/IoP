import time
import tools.logger
from models.plant import Plant
from models.sensor import Sensor

from tools.sensor import ToolChainSensor
from sensor_scripts.driver.mcp3008 import mcp3008


class GenericMoisture(object):
  """docstring for GenericMoisture"""

  def __init__(self):
    super(GenericMoisture, self).__init__()

  @staticmethod
  def run(samples=10):
    values = []
    for i in range(0, samples):
      values.append(mcp3008().read_pct(0))
      time.sleep(.2)

    average = sum(values) / float(len(values))
    if average != 0:
      tools = ToolChainSensor()
      plant = Plant.get(Plant.localhost == True)

      moisture = {'sensor': Sensor.get(Sensor.name == 'moisture'),
                  'plant': plant,
                  'value': average}

      if tools.insert_data(moisture):
        tools.set_hardware(moisture)

if __name__ == '__main__':
  GenericMoisture.run()
