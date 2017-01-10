# from ...driver.mcp23017 import MCP230XX_GPIO
# from pymongo import MongoClient
# from ...tools.main import Tools
import time
# import smbus
from tools.main import VariousTools
from sensor_scripts.driver.mcp23017 import MCP230XX_GPIO
from models.sensor import Sensor, SensorStatus
from models.plant import Plant


class MoistureBar:
  def __init__(self):
    pass

  @staticmethod
  def run():
    result = VariousTools.offline_check('ledbar', hardware=True, pins=[0, 1, 2, 3, 4, 5], mcp=True)
    if result is True:
      sensor = Sensor.get(Sensor.name == 'moisture')
      plant = Plant.get(Plant.localhost == True)
      status = SensorStatus.get(SensorStatus.sensor == sensor,
                                SensorStatus.plant == plant)

      # init MCP230xx GPIO adapter.
      bus = 1
      gpio_count = 16
      address = 0x20

      # Create MCP230xx GPIO adapter.
      mcp = MCP230XX_GPIO(bus, address, gpio_count)

      # GREEN 5/6
      # YELLOW 3/4
      # RED 1/2
      led = 0
      for i in [['threat', 1, 2], ['cautioning', 3, 4], ['optimum', 5, 6]]:
        if status.level.label == i[0]:
          led = i[2] if status.status is True else i[1]

      pins = [0, 1, 2, 3, 4, 5]
      for pin in pins:
        mcp.setup(pin, mcp.OUT)

      for i in range(5, led - 1, -1):
        mcp.output(i, 0)  # Pin 0 Low
        time.sleep(round((1.35**i) / 10, 3))

      for i in range(0, led):
        mcp.output(i, 1)  # Pin 0 High
        time.sleep(round((1.35**i) / 10, 3))

if __name__ == "__main__":
  MoistureBar.run()
