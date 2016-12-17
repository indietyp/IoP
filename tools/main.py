from models.sensor import *
from models.context import DayNightTime
import sys
import datetime


class MeshString(str):
  def rreplace(self, old, new, maxcount=sys.maxsize):
    """ reverse replace
        reverses string and runs replace at reversed old and new
        returns reversed reversed string
    """
    self = self[::-1].replace(old[::-1], new[::-1], maxcount)[::-1]
    return self


class VariousTools(object):
  """docstring for VariousTools"""

  def __init__(self):
    pass

  def get_satisfaction_ranges(self, sensor, plant):
    """ INPUT sensor (object)
        INPUT plant (object)

        OUTPUT (dict):
          'danger': min, max
          'warning': min, max
          'optima': min, max
    """
    output = {}
    output['danger'] = {'min': sensor.min_value, 'max': sensor.max_value}

    # sat_lvl == satisfaction_level
    # only shortcut
    for sat_lvl in SensorSatisfactionLevel.select():
      key = sat_lvl.label
      output[key] = {'min': sat_lvl.min_value, 'max': sat_lvl.max_value}

    return output

  @staticmethod
  def offline_check(mode, hardware=True, pins=[], mcp=False):
    online = True

    for time in DayNightTime.select():
      mode = getattr(time, mode)
      if mode is True:
        if not (datetime.time.(str(time.stop), '%-H%M') <= datetime.time.now() >= datetime.time.strptime(str(time.start), '%-H%M')):
          online = False

    if online is False:
      if hardware and not mcp:
        from GPi.GPIO import GPIO
        for pin in pins:
          GPIO.output(pin, False)
      elif hardware and mcp:
        from sensor_scripts.driver.mcp23017 import MCP230XX_GPIO
        mcp = MCP230XX_GPIO(1, 32, 16)
        for pin in pins:
          mcp.output(pin, False)

    return online
