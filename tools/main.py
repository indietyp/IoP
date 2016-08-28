from models.sensor import *
import sys


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
