from models.sensor import SensorData
from models.sensor import Sensor
from models.sensor import Plant
from models.sensor import SensorHardwareConnector
from models.sensor import *

from mesh_network.dedicated import MeshDedicatedDispatch

# from tools.mesh import ToolChainMeshSender
from tools.hardware import ToolChainHardware
from tools.forecast import SensorDataForecast


class ToolChainSensor(object):
  """Tool Chain for sensors"""

  def __init__(self):
    pass

  def get_last_persistant(self, current, plant, counter=0):
    # WHERE PLANT
    persistant = False
    try:
      previous = SensorData.select() \
                           .where(SensorData.sensor == current.sensor) \
                           .where(SensorData.plant == plant) \
                           .order_by(SensorData.created_at.desc())[counter]
    except IndexError:
      print('ERROR')
      persistant = True
      return persistant

    counter += 1

    if previous.persistant is True:
      persistant = False if counter % 7 != 0 else True
      return persistant
    else:
      return self.get_last_persistant(previous, plant, counter)

  def get_second_last_entry(self, current, plant):
    try:
      previous = SensorData.select() \
                           .where(SensorData.sensor == current.sensor) \
                           .where(SensorData.plant == plant) \
                           .order_by(SensorData.created_at.desc())[1]
    except:
      return None

    return previous

  def delete_non_persistant_overflow(self, sensor, plant):
    deleted = 0
    non_persistant = SensorData.select() \
                               .where(SensorData.sensor == sensor) \
                               .where(SensorData.plant == plant) \
                               .where(SensorData.persistant == False) \
                               .order_by(SensorData.created_at.asc())
                               # .order_by(SensorData.created_at.desc())

    overflow = non_persistant.count() - plant.persistant_hold
    overflow = int(overflow)

    if overflow > 0:
      for dataset in non_persistant[:overflow]:
        deleted += dataset.delete_instance()

    return deleted

  def get_sensor_satification_value(self, data):
    """ dict of data:
          'sensor': object of sensor
          'value': value - float
          'plant': current selected plant
    """
    pl = data['plant']
    se = data['sensor']
    cl = SensorSatisfactionValue.select()\
                                .where(SensorSatisfactionValue.plant == pl)\
                                .where(SensorSatisfactionValue.sensor == se)
    collection = cl

    return collection

  def modify_sensor_status(self, data):
    """ dict of data:
          'sensor': object of sensor
          'value': value - float
          'plant': current selected plant
    """
    collection = self.get_sensor_satification_value(data)

    current = [0]

    for satisfaction in collection:
      if satisfaction.inherited is True:
        min_value = satisfaction.sensor.min_value
        max_value = satisfaction.sensor.max_value
      else:
        min_value = satisfaction.min_value
        max_value = satisfaction.max_value

      if min_value <= data['value'] <= max_value:
        barrier = max_value - min_value / 2
        high_low = True if data['value'] >= barrier else False

        if min_value >= current[0]:
          current[0] = min_value
          status, result = SensorStatus.get_or_create(
              sensor=data['sensor'],
              plant=data['plant'],
              defaults={'level': satisfaction.level})

          status.level = satisfaction.level
          status.status = high_low
          status.save()

          # not rlly working?
          # counter, result = SensorCount.get_or_create(
          #     plant=data['plant'],
          #     sensor=data['sensor'],
          #     level=satisfaction.level,
          #     defaults={'count': int(0)})
          # counter.count += 1
          # counter.save()

    return 'success'

  def insert_data(self, data):
    """ dict of data:
          'sensor': object of sensor
          'value': value - float
          'plant': current selected plant
    """
    current_entries = SensorData.select()\
                                .where(SensorData.sensor == data['sensor'])\
                                .count()

    persistant = False

    sensor_db = SensorData()
    sensor_db.value = round(data['value'], 2)
    sensor_db.plant = data['plant']
    sensor_db.sensor = data['sensor']
    sensor_db.persistant = False
    sensor_db.save()

    last_entry = self.get_second_last_entry(sensor_db, data['plant'])
    last_value = last_entry.value if last_entry is not None else data['value']

    offset = abs(data['value'] - last_value)
    if offset >= data['sensor'].persistant_offset:
      persistant = True
    elif current_entries > 6:
      persistant = self.get_last_persistant(sensor_db, data['plant'], 1)

    sensor_db.persistant = persistant
    sensor_db.save()

    self.delete_non_persistant_overflow(data['sensor'], data['plant'])
    data['satisfaction'] = self.modify_sensor_status(data)

    # CALL modify_sensor_satisfaction MARKING
    # --> is calling
    # --> add_sensor_current_status

    if persistant is True:
      SensorDataForecast().run(data)
      MeshDedicatedDispatch().new_data(data['sensor'])

    return persistant

  def set_hardware(self, data):
    pass
    hardware = SensorHardware.select()

    hardware = SensorHardwareConnector.select() \
                                      .where(SensorHardwareConnector.sensor == data['sensor'])

    data['satisfaction'] = SensorStatus.get(
        SensorStatus.sensor == data['sensor'],
        SensorStatus.plant == data['plant'])

    hardware_toolchain = ToolChainHardware()
    for piece in hardware:
      exec('hardware_toolchain.{}(data)'.format(piece.hardware.function))

    # get hardware -> call function (in database?)
