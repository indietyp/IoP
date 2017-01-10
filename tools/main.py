from models.sensor import *
from models.context import DayNightTime
from settings.database import DATABASE_NAME
import os
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
        start = str(time.start) if len(str(time.start)) > 3 else '0' + str(time.start)
        stop = str(time.stop) if len(str(time.stop)) > 3 else '0' + str(time.stop)
        if not (datetime.time(hour=int(start[0:2]), minute=int(start[2:4])) <= datetime.datetime.now().time() <= datetime.time(hour=int(stop[0:2]), minute=int(stop[2:4]))):
          online = False

    if online is False:
      if hardware and not mcp:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in pins:
          GPIO.setup(pin, GPIO.OUT)
          GPIO.output(pin, False)
      elif hardware and mcp:
        from sensor_scripts.driver.mcp23017 import MCP230XX_GPIO
        mcp = MCP230XX_GPIO(1, 0x20, 16)
        for pin in pins:
          mcp.setup(pin, mcp.OUT)
          mcp.output(pin, False)

    return online

  @staticmethod
  def verify_database():
    return os.path.isfile(DATABASE_NAME)
