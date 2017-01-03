import sys
import json
import logging
import datetime
import urllib.request

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
    cl = SensorSatisfactionValue.select() \
                                .where(SensorSatisfactionValue.plant == pl) \
                                .where(SensorSatisfactionValue.sensor == se) \
                                .dicts()
    collection = list(cl)

    return collection

  def modify_sensor_status(self, data):
    """ dict of data:
          'sensor': object of sensor
          'value': value - float
          'plant': current selected plant
    """
    collection = self.get_sensor_satification_value(data)

    current = [- sys.maxsize, '', '']

    for satisfaction in collection:
      if satisfaction['inherited'] is True:
        min_value = data['sensor'].min_value
        max_value = data['sensor'].max_value
      else:
        min_value = satisfaction['min_value']
        max_value = satisfaction['max_value']

      if min_value <= data['value'] <= max_value:
        barrier = max_value - min_value / 2
        high_low = True if data['value'] >= barrier else False

        if min_value >= current[0]:
          current[0] = min_value
          current[1] = satisfaction
          current[2] = SensorStatus.get(SensorStatus.sensor == data['sensor'],
                                        SensorStatus.plant == data['plant'])

          status, result = SensorStatus.get_or_create(
              sensor=data['sensor'],
              plant=data['plant'],
              defaults={'level': satisfaction['level']})

          status.level = satisfaction['level']
          status.status = high_low
          status.save()

          # not rlly working?
          counter, result = SensorCount.get_or_create(
              plant=data['plant'],
              sensor=data['sensor'],
              level=satisfaction['level'],
              defaults={'count': int(0)})
          counter.count += 1
          counter.save()

    if current[2].level == current[1]['level']:
      data['plant'].sat_streak = data['plant'].sat_streak + 1
      data['plant'].save()
      url = 'add'
    else:
      data['plant'].sat_streak = 1
      data['plant'].save()
      url = 'reset'

    for external in Plant.select().where(Plant.localhost == False):
      try:
        with urllib.request.urlopen('http://{}:2902/update/plant/{}/satisfaction/level/{}'.format(external.ip, str(data['plant'].uuid), url)) as response:
          data = json.loads(response.read().decode('utf8'))
          logger.debug(data)
      except:
        pass

    return 'success'

  def insert_data(self, data, mesh=True, prediction=True):
    """ dict of data:
          'sensor': object of sensor
          'value': value - float
          'plant': current selected plant
    """
    between = datetime.datetime.now()
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
    logger.debug('(160-175) time elapsed: {}'.format(datetime.datetime.now() - between))

    between = datetime.datetime.now()
    last_entry = self.get_second_last_entry(sensor_db, data['plant'])
    last_value = last_entry.value if last_entry is not None else data['value']
    logger.debug('(177-180) time elapsed: {}'.format(datetime.datetime.now() - between))

    between = datetime.datetime.now()
    offset = abs(data['value'] - last_value)
    if offset >= data['sensor'].persistant_offset:
      persistant = True
    elif current_entries > 6:
      persistant = self.persistant_evaluation(data['plant'], data['sensor'])

    sensor_db.persistant = persistant
    sensor_db.save()
    logger.debug('(182-191) time elapsed: {}'.format(datetime.datetime.now() - between))

    between = datetime.datetime.now()
    self.delete_non_persistant_overflow(data['sensor'], data['plant'])
    data['satisfaction'] = self.modify_sensor_status(data)
    logger.debug('(193-196) time elapsed: {}'.format(datetime.datetime.now() - between))

    logger.debug('{} - {} persistant: {}'.format(data['plant'].name, data['sensor'].name, persistant))
    between = datetime.datetime.now()
    if persistant is True:
      if prediction:
        SensorDataForecast().run(data)

      if mesh:
        logger.debug('running mesh')
        from mesh_network.dedicated import MeshDedicatedDispatch
        MeshDedicatedDispatch().new_data(data['sensor'])
    logger.debug('(199-208) time elapsed: {}'.format(datetime.datetime.now() - between))
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
