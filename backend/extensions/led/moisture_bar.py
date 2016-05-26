from ...driver.mcp23017 import MCP230XX_GPIO
from pymongo import MongoClient
from ...tools.main import Tools
import smbus
import time
class StatusBar:
  def __init__(self, plant, value):
    self.client = MongoClient()
    self.db = self.client.pot
    self.plants = self.db.Plant
    self.plant = self.plants.find_one({"abbreviation": plant})
    self.value = value

  def calculate(self, ranges, state):
    if state['color'] == 'green':
      if self.value <= (((ranges['green']['min'] - ranges['green']['max']) / 3) * 2):
        led = 6
      else:
        led = 5

    elif state['color'] == 'yellow':
      differenceLow = (ranges['green']['min'] - ranges['yellow']['min'] ) / 2
      differenceHigh = (ranges['yellow']['max'] - ranges['green']['max'] ) / 2
      if (self.value <= (ranges['yellow']['min'] + differenceLow) and state['status'] == 'low') or (self.value >= (ranges['green']['max'] + differenceHigh) and state['status'] == 'high'):
        led = 3
      else:
        led = 4

    else:
      differenceLow = (ranges['yellow']['min'] - ranges['red']['min']) / 2
      differenceHigh = (ranges['red']['max'] - ranges['yellow']['max']) / 2
      if (self.value <= (ranges['red']['min'] + differenceLow) and state['status'] == 'low') or (self.value >= (ranges['yellow']['min'] + differenceHigh) and state['status'] == 'high'):
        led = 1
      else:
        led = 2

    return led

  def setStatus(self):
    toolChain = Tools(self.db, self.plant)
    dataRange = toolChain.getOptions('m')
    mcpPins = toolChain.getPins('mcp')

    state = toolChain.checkOptions(self.value, dataRange)
    led = self.calculate(dataRange, state)

    bus = self.db.ExternalDevices.find_one({'n': 'mcp23017'})['a']['bus']
    gpio_count = self.db.ExternalDevices.find_one({'n': 'mcp23017'})['a']['pins']
    address = self.db.ExternalDevices.find_one({'n': 'mcp23017'})['p']['address']

    # Create MCP230xx GPIO adapter.
    mcp = MCP230XX_GPIO(bus, address, gpio_count)
    mcp.setmode(mcp.BCM)

    for pin in mcpPins:
      mcp.setup(pin, mcp.OUT)

    for i in range(5, led-1, -1):
      mcp.output(i, 0)  # Pin 0 Low
      time.sleep(0.2)
    for i in range(0,led):
      mcp.output(i, 1)  # Pin 0 High
      time.sleep(0.2)

if __name__ == "__main__":
  test = StatusBar('m', 70)
  test.setStatus()
