import sys
import json
import logging
import datetime
import urllib.request
import urllib.parse

from models.sensor import SensorData
from models.sensor import Sensor
from models.sensor import Plant
from models.sensor import SensorHardwareConnector
from models.sensor import *

# from tools.mesh import ToolChainMeshSender
# from tools.hardware import ToolChainHardware
import tools.logger
from tools.forecast import SensorDataForecast
logger = logging.getLogger('sensor_scripts')


class ToolChainSensor(object):
  """Tool Chain for sensors"""

  def __init__(self):
    pass

  def mail_evaluation(self, data):
    if data['satisfaction'].level.label == 'threat':
      message = SensorDangerMessage()
      message.plant = data['plant']
      message.sensor = data['sensor']
      message.level = data['satisfaction'].level

      message.message = '---'
      message.value = data['value']

      message.save()

  def persistant_evaluation(self, plant, sensor):
    dataset = SensorData.select(SensorData.created_at) \
                        .where(SensorData.sensor == sensor) \
                        .where(SensorData.plant == plant) \
                        .where(SensorData.persistant == True) \
                        .order_by(SensorData.created_at.desc()) \
                        .limit(1) \
                        .dicts()

    if dataset.count() == 0:
      return True
    else:
      dataset = list(dataset)[0]
      if datetime.datetime.now() - dataset['created_at'] >= datetime.timedelta(minutes=29):
        return True
      else:
        return False

  def get_second_last_entry(self, current, plant):
    try:
      previous = SensorData.select() \
                           .where(SensorData.sensor == current.sensor) \
                           .where(SensorData.plant == plant) \
                           .order_by(SensorData.created_at.desc()) \
                           .limit(2)[1]
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
    cl = SensorSatisfactionValue.select() \
                                .where(SensorSatisfactionValue.plant == pl) \
                                .where(SensorSatisfactionValue.sensor == se) \
                                .dicts()
    collection = list(cl)

    return collection

  def evaluate_sensor_status(self, data):
    evl = {'threat': 0, 'cautioning': 0, 'optimum': 0}
    status_all = SensorStatus.select().where(SensorStatus.plant == data['plant'])

    for status in status_all:
      evl[status.level.label] += 1

    if evl['threat'] > 0:
      return 3
    elif evl['cautioning'] > 0:
      return 2
    elif evl['optimum'] > 0:
      return 1

  def modify_sensor_status(self, data, mesh=True):
    """ dict of data:
          'sensor': object of sensor
          'value': value - float
          'plant': current selected plant
    """
    collection = self.get_sensor_satification_value(data)

    current = {'minimum': - sys.maxsize,
               'satisfaction': None}

    for satisfaction in collection:
      if satisfaction['inherited']:
        satisfaction['min_value'] = data['sensor'].min_value
        satisfaction['max_value'] = data['sensor'].max_value

      if current['minimum'] < satisfaction['min_value']:
        if satisfaction['min_value'] <= data['value'] <= satisfaction['max_value']:
          current['satisfaction'] = satisfaction
          current['minimum'] = satisfaction['min_value']

    status = SensorStatus.get(SensorStatus.sensor == data['sensor'],
                              SensorStatus.plant == data['plant'])

    previous = self.evaluate_sensor_status(data)
    if status.level.id != current['satisfaction']['level']:
      barrier = current['satisfaction']['max_value'] - current['satisfaction']['min_value']
      barrier = True if data['value'] >= barrier else False

      status.level = current['satisfaction']['level']
      status.status = barrier
      status.save()

    if previous == self.evaluate_sensor_status(data):
      data['plant'].sat_streak = data['plant'].sat_streak + 1
    else:
      data['plant'].sat_streak = 1
    data['plant'].save()

    counter, result = SensorCount.get_or_create(
        plant=data['plant'],
        sensor=data['sensor'],
        level=satisfaction['level'],
        defaults={'count': int(0)})
    counter.count = counter.count + 1
    counter.save()

    return status

  def insert_data(self, data, mesh=True, prediction=True):
    """ dict of data:
          'sensor': object of sensor
          'value': value - float
          'plant': current selected plant
    """
    start = datetime.datetime.now()
    current_entries = SensorData.select()\
                                .where(SensorData.sensor == data['sensor'])\
                                .count()

    persistant = False
    data['value'] = round(data['value'], 2)

    sensor_db = SensorData()
    sensor_db.value = data['value']
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
      persistant = self.persistant_evaluation(data['plant'], data['sensor'])

    sensor_db.persistant = persistant
    sensor_db.save()

    self.delete_non_persistant_overflow(data['sensor'], data['plant'])
    logger.debug('{} - {} persistant: {}'.format(data['plant'].name, data['sensor'].name, persistant))

    if persistant:
      data['satisfaction'] = self.modify_sensor_status(data, mesh)
      self.mail_evaluation(data)

      if prediction:
        SensorDataForecast().run(data)

      if mesh:
        from mesh_network.dedicated import MeshDedicatedDispatch
        MeshDedicatedDispatch().new_data(data['sensor'], plant=data['plant'])

        if data['plant'].localhost:
          slaves = Plant.select().where(Plant.role == str(data['plant'].uuid))
          slaves = list(slaves)

          for slave in slaves:
            print('slaved')
            MeshDedicatedDispatch().slave_data(slave, data['sensor'])

    logger.debug('time elapsed: {}'.format(datetime.datetime.now() - start))
    return persistant

  def set_hardware(self, data):
    hardware = SensorHardware.select()

    hardware = SensorHardwareConnector.select() \
                                      .where(SensorHardwareConnector.sensor == data['sensor'])

    data['satisfaction'] = SensorStatus.get(
        SensorStatus.sensor == data['sensor'],
        SensorStatus.plant == data['plant'])

    from tools.hardware import ToolChainHardware
    hardware_toolchain = ToolChainHardware()
    for piece in hardware:
      exec('hardware_toolchain.{}(data)'.format(piece.hardware.function))
