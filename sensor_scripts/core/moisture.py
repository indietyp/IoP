import time
import tools.logger
import RPi.GPIO as GPIO
from models.plant import Plant
from models.sensor import Sensor

from tools.sensor import ToolChainSensor
from sensor_scripts.driver.mcp3002 import mcp3002


class GenericMoisture(object):
  """docstring for GenericMoisture"""

  def __init__(self):
    super(GenericMoisture, self).__init__()

  @staticmethod
  def run(samples=10):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)
    GPIO.output(4, True)

    values = []
    for i in range(0, samples):
      values.append(mcp3002().read_pct(0, 1))
      time.sleep(.2)
    print(values)
    GPIO.output(4, False)

    average = sum(values) / float(len(values))
    if average != 0:
      tools = ToolChainSensor()
      plant = Plant.get(localhost=True)

      moisture = {'sensor': Sensor.get(Sensor.name == 'moisture'),
                  'plant': plant,
                  'value': average}

      if tools.insert_data(moisture):
        tools.set_hardware(moisture)

if __name__ == '__main__':
  GenericMoisture.run()
