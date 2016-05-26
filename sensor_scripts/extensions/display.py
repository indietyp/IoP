from collections import OrderedDict
from pymongo import MongoClient
import pymongo
from ..driver.char_lcd import Adafruit_CharLCD
from ..driver.mcp23017 import MCP230XX_GPIO


class Display:
  def __init__(self):
    self.client = MongoClient()
    self.db = self.client.pot

    self.data = {
                  'sensor': OrderedDict([
                    ('temperature', {
                     'name': [],
                     'value': [],
                     'unit': []
                    }),
                    ('humidity', {
                      'name': [],
                      'value': [],
                      'unit': []
                    }),
                    ('moisture', {
                      'name': [],
                      'value': [],
                      'unit': []
                    }),

                    ('light', {
                      'name': [],
                      'value': [],
                      'unit': []
                    })
                  ]),
                  'display': {
                    'length': 0,
                    'lines': 0,
                    'pins': {},
                    'text': ''
                  }
                }
  def calculate(self):
    for i in range(0, self.data['display']['lines']):
      sensorDataList = []

      sensorDataList = self.data['sensor'].values()[i]['name'][0:(self.data['display']['length'] - 5)]
      sensorDataList = [ x.upper() for x in sensorDataList ]
      sensorDataList += [" "," "]
      sensorDataList += self.data['sensor'].values()[i]['value']
      sensorDataList += self.data['sensor'].values()[i]['unit']

      if len(sensorDataList) < self.data['display']['length']:
        rest = self.data['display']['length'] - len(sensorDataList)
        for x in range(0,rest):
          sensorDataList.insert(len(sensorDataList) - 5, ' ')

      self.data['display']['text'] += ''.join(sensorDataList)
      self.data['display']['text'] += '\n' if i != (self.data['display']['lines'] - 1) else ''
  def get(self):
    self.data['sensor']['temperature']['name'] = list(self.db.SensorType.find_one({"a": "t"})['t'])
    self.data['sensor']['moisture']['name'] = list(self.db.SensorType.find_one({"a": "m"})['t'])
    self.data['sensor']['humidity']['name'] = list(self.db.SensorType.find_one({"a": "h"})['t'])
    self.data['sensor']['light']['name'] = list(self.db.SensorType.find_one({"a": "l"})['t'])

    self.data['sensor']['temperature']['value'] = list("{0:0=2d}".format(int(self.db.SensorData.find({'p': 'm', 's': 't'}).sort([('_id', pymongo.DESCENDING)])[0]['v'])))
    self.data['sensor']['moisture']['value'] = list("{0:0=2d}".format(int(self.db.SensorData.find({'p': 'm', 's': 'm'}).sort([('_id', pymongo.DESCENDING)])[0]['v'])))
    self.data['sensor']['humidity']['value'] = list("{0:0=2d}".format(int(self.db.SensorData.find({'p': 'm', 's': 'h'}).sort([('_id', pymongo.DESCENDING)])[0]['v'])))
    self.data['sensor']['light']['value'] = list("{0:0=2d}".format(int(self.db.SensorData.find({'p': 'm', 's': 'l'}).sort([('_id', pymongo.DESCENDING)])[0]['v'])))

    self.data['sensor']['temperature']['unit'] = ['C']
    self.data['sensor']['moisture']['unit'] = ['%']
    self.data['sensor']['humidity']['unit'] = ['%']
    self.data['sensor']['light']['unit'] = ['l']

    self.data['display']['length'] = self.db.ExternalDevices.find_one({'n': 'display'})['a']['length']
    self.data['display']['lines'] = self.db.ExternalDevices.find_one({'n': 'display'})['a']['lines']

  def set(self):
    bus = self.db.ExternalDevices.find_one({'n': 'mcp23017'})['a']['bus']
    gpio_count = self.db.ExternalDevices.find_one({'n': 'mcp23017'})['a']['pins']
    address = self.db.ExternalDevices.find_one({'n': 'mcp23017'})['p']['address']

    pins = self.db.ExternalDevices.find_one({'n': 'display'})['p']['mcp']

    self.get()
    self.calculate()

    # Create MCP230xx GPIO adapter.
    mcp = MCP230XX_GPIO(bus, address, gpio_count)

    # Create LCD, passing in MCP GPIO adapter.
    lcd = Adafruit_CharLCD(pin_rs=11, pin_e=10, pins_db=pins['pins_db'], GPIO=mcp)
    # lcd = Adafruit_CharLCD(pin_rs=11, pin_e=10, pins_db=[12,13,14,15])

    lcd.clear()
    lcd.message(self.data['display']['text'])
    #lcd.message('test')

    # print self.data['display']['text']
if __name__ == "__main__":
  tester = Display()
  tester.set()


