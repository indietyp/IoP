from models.plant import Plant
from models.sensor import SensorData, SensorDataPrediction
from tools.sensor import ToolChainSensor
from tools.forecast import SensorDataForecast
from mesh_network.dedicated import MeshDedicatedDispatch
import random
import datetime


class PlantSimulate:
  def __init__(self):
    pass

  def __retrieve_data(self, target, source, sensor):
    data = SensorData.select().where(SensorData.plant == target,
                                     SensorData.sensor == sensor)\
                              .order_by(SensorData.created_at.desc())
    saved = True

    if data.count() < 1:
      saved = False
      data = SensorData.select().where(SensorData.plant == source,
                                       SensorData.sensor == sensor)\
                                .order_by(SensorData.created_at.desc())

      if data.count() > 1000:
        offset = random.randint(0, data.count() - 1000)
        data = data.offset(offset).limit(1000)

      time = datetime.datetime.now()
      for sample in data:
        new = SensorData()
        new.value = sample.value
        new.plant = target
        new.sensor = sample.sensor
        new.created_at = time
        new.save()

        time -= datetime.timedelta(minutes=30)

      saved = True

    return data, saved

  def run(self, target, sensor, source=None):
    if source is None:
      source = Plant.get(Plant.localhost == True)

    predicted = SensorDataPrediction.select().where(SensorDataPrediction.plant == target,
                                                    SensorDataPrediction.sensor == sensor)

    if predicted.count() == 0:
      data, saved = self.__retrieve_data
      data = data.order_by(SensorData.created_at.asc())
      forecast = SensorDataForecast()

      information = {'plant': target, 'sensor': sensor}
      information['prediction'] = forecast.predict(information, data)
      forecast.insert_database(information)

      print(information)

    predicted = SensorDataPrediction.select().where(SensorDataPrediction.plant == target,
                                                    SensorDataPrediction.sensor == sensor) \
                                             .order_by(SensorDataPrediction.created_at.asc()) \
                                             .limit(1)

    for sample in predicted:
      if sample.time >= datetime.datetime.now():
        releaser = True
        ToolChainSensor().insert_data({'sensor': sensor, 'plant': target, 'value': sample.value})
        # insert hardware? -- test if DUMMYPLANT hardware?
        sample.delete_instance()
      else:
        released = False
        print('not in prediction timeframe')
    return released
