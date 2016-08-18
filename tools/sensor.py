from models.sensor import SensorData
from models.sensor import Sensor
from models.sensor import Plant

# from tools.mesh import ToolChainMeshSender


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
                               .order_by(SensorData.created_at.desc())

    overflow = non_persistant.count() - sensor.persistant_hold
    print('offset' + str(sensor.persistant_hold))
    overflow = int(overflow)
    # print('overflow: ' + str(overflow))
    if overflow > 0:
      for dataset in non_persistant[:overflow]:
        deleted += dataset.delete_instance()

    return deleted

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

    print('deleted: ' + str(self.delete_non_persistant_overflow(data['sensor'], data['plant'])))

    # CALL MESH SCRIPT FOR SYNCING!
    # ToolChainMeshSender.notify_data(sensor_db)
    return persistant

  def set_hardware(self, data):
    pass
