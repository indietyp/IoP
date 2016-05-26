from pymongo import MongoClient
import pymongo
from ..driver.mcp23017 import MCP230XX_GPIO


client = MongoClient('bilalmahmoud.de' , 27017)
db. = client.pot

bus = db.ExternalDevices.find_one({'n': 'mcp23017'})['a']['bus']
gpio_count = db.ExternalDevices.find_one({'n': 'mcp23017'})['a']['pins']
address = db.ExternalDevices.find_one({'n': 'mcp23017'})['p']['address']

mcp = MCP230XX_GPIO(bus, address, gpio_count)
mcp.setmode(mcp.BCM)

for i in range(0, gpio_count):
  mcp.setup(pin, mcp.OUT)
  mcp.output(i, 0)  # Pin i Low

