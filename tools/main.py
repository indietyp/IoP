from models.sensor import *


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

  def check_sensor_value_for_satisfaction_range(self, data):
    """ INPUT data (dict):
          'sensor': object of sensor
          'value': value - float
          'plant': current selected plant

        OUTPUT (object)
    """
    ranges = self.get_satisfaction_ranges(data['sensor'], data['plant'])
    print(ranges)

  def csvfsr(self):
    return self.check_sensor_value_for_state()

  def modify_current_sensor_satisfaction(self, data):
    """ INPUT data (dict):
          'sensor': object of sensor
          'value': value - float
          'plant': current selected plant
        OUTPUT (object):
          sensorsatisfaction
    """

    pass
