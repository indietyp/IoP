import re
import logging
import datetime
import tools.logger
from models.plant import Plant
from collections import OrderedDict
from tools.main import VariousTools
from models.sensor import Sensor, SensorData, SensorHardware
from sensor_scripts.driver.mcp23017 import MCP230XX_GPIO
from sensor_scripts.driver.char_lcd import Adafruit_CharLCD
logger = logging.getLogger('sensor_scripts')


class Display:
  def __init__(self):
    # name
    # value
    # unit
    # raw

    self.data = {
        'sensor': OrderedDict([
            ('temperature', {}),
            ('humidity', {}),
            ('moisture', {}),
            ('light', {})
        ]),
        'display': {
            'length': 8,
            'lines': 2,
            'pins': {'pin_e': 11, 'pins_db': [12, 13, 14, 15], 'pin_rs': 10},
            'text': ''
        }
    }

  def calculate(self):
    sensor_values = list(self.data['sensor'].values())

    for i in range(0, self.data['display']['lines']):
      display_list = []

      list_end = self.data['display']['length'] - 5
      display_list = sensor_values[i]['name'][0:list_end]

      display_list = [char.upper() for char in display_list]
      display_list += [" ", " "]

      value = round(sensor_values[i]['value'], 0)
      value = int(value)
      display_list += str(value)
      display_list += sensor_values[i]['unit'] if sensor_values[i]['name'] != 'temperature' else 'C'

      if len(display_list) < self.data['display']['length']:
        rest = self.data['display']['length'] - len(display_list)
        for x in range(0, rest):
          display_list.insert(len(display_list) - 5, ' ')

      display_list.append(
          '\n' if i != self.data['display']['lines'] - 1 else '')

      self.data['display']['text'] += ''.join(display_list)

    # print(self.data['display']['text'])

    return self

  def get(self):
    sensors = self.data['sensor']
    plant = Plant.select().where(Plant.localhost == True)[0]

    for sensor in sensors:
      sensors[sensor]['raw'] = Sensor.get(Sensor.name == sensor)

      sensors[sensor]['name'] = sensors[sensor]['raw'].name

      unit = sensors[sensor]['raw'].unit
      sensors[sensor]['unit'] = re.sub(r'(?!%)\W+', '', unit)[0]

      order = SensorData.created_at.desc()
      r_sen = sensors[sensor]['raw']
      sensors[sensor]['value'] = SensorData.select()\
                                           .where(SensorData.plant == plant)\
                                           .where(SensorData.sensor == r_sen)\
                                           .order_by(order)[0].value

    self.data['sensor'] = sensors

    return self

  def set(self):
    result = VariousTools.offline_check('display', hardware=False)
    if result is True:
      execute = False
      sensor = SensorHardware.get(label='display')

      if sensor.last_execution is not None:
        offset = datetime.datetime.now() - sensor.last_execution
        if offset.seconds >= 30 * 60:
          execute = True
      else:
        execute = True

      if execute is True:
        sensor.last_execution = datetime.datetime.now()
        sensor.save()

        logger.debug('display: updated')

        bus = 1
        gpio_count = 16
        address = 0x20

        self.get()
        self.calculate()

        # Create MCP230xx GPIO adapter.
        mcp = MCP230XX_GPIO(bus, address, gpio_count)

        # Create LCD, passing in MCP GPIO adapter.
        lcd = Adafruit_CharLCD(pin_rs=11, pin_e=10, pins_db=[12, 13, 14, 15], GPIO=mcp)

        lcd.clear()
        lcd.message(self.data['display']['text'])
      else:
        logger.debug('display: not updated')

      # print self.data['display']['text']
    else:
      logger.info('display: in offline timeframe - clearing')
      bus = 1
      gpio_count = 16
      address = 32

      mcp = MCP230XX_GPIO(bus, address, gpio_count)
      lcd = Adafruit_CharLCD(pin_rs=11, pin_e=10, pins_db=[12, 13, 14, 15], GPIO=mcp)
      lcd.clear()


if __name__ == "__main__":
  Display().set()
