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

    logger.debug('status level: {}'.format(status.level))
    logger.debug('status level id: {}'.format(status.level.id))
    logger.debug('current level: {}'.format(current['satisfaction']['level']))
    if status.level.id != current['satisfaction']['level']:
      barrier = current['satisfaction']['max_value'] - current['satisfaction']['min_value']
      barrier = True if data['value'] >= barrier else False

      status.level = current['satisfaction']['level']
      status.status = barrier
      status.save()

      data['plant'].sat_streak = 1
      data['plant'].save()
      url = 'reset'

    else:
      data['plant'].sat_streak = data['plant'].sat_streak + 1
      data['plant'].save()
      url = 'add'

    if mesh:
      for external in Plant.select().where(Plant.localhost == False):
        try:
          magic = urllib.parse.urlencode({}).encode()
          req = urllib.request.Request('http://{}:2902/update/plant/{}/satisfaction/level/{}'.format(external.ip, str(data['plant'].uuid), url), data=magic)
          with urllib.request.urlopen(req) as response:
            output = json.loads(response.read().decode('utf8'))
            logger.debug(output)
        except:
          logger.debug('couldn\'t access {}'.format(external.name))

    counter, result = SensorCount.get_or_create(
        plant=data['plant'],
        sensor=data['sensor'],
        level=satisfaction['level'],
        defaults={'count': int(0)})
    counter.count = counter.count + 1
    counter.save()

    return 'success'

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
    # start block
    ###################
    if persistant:
      self.modify_sensor_status(data, mesh)

      if prediction:
        SensorDataForecast().run(data)

      if mesh:
        from mesh_network.dedicated import MeshDedicatedDispatch
        MeshDedicatedDispatch().new_data(data['sensor'])
    ###################
    # 60.02 seconds
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
