import random
import datetime
from models.plant import Plant, db
from tools.sensor import ToolChainSensor
from tools.forecast import SensorDataForecast
from models.sensor import SensorData, SensorDataPrediction


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
                                       SensorData.sensor == sensor) \
                                .order_by(SensorData.created_at.desc())

      if data.count() > 1000:
        offset = random.randint(0, data.count() - 1000)
        data = data.offset(offset).limit(1000)

      data = data.dicts()
      prepared = list(data)

      current = datetime.datetime.now()
      for sample in prepared:
        sample['plant'] = target
        sample['created_at'] = current

        current -= datetime.timedelta(minutes=30)

      print(len(prepared))

      with db.atomic():
        for idx in range(0, len(prepared), 100):
          SensorData.insert_many(prepared[idx:idx + 100]).execute()

      data = SensorData.select().where(SensorData.plant == target,
                                       SensorData.sensor == sensor) \
                                .order_by(SensorData.created_at.desc())

      saved = True

    return data, saved

  @staticmethod
  def run(self, target, sensor, source=None):
    if source is None:
      count = 0
      for plant in Plant.select():
        current = SensorData.select().where(SensorData.plant == target,
                                            SensorData.sensor == sensor) \
                                     .count()
        if count < current:
          count = current
          target = plant

    predicted = SensorDataPrediction.select().where(SensorDataPrediction.plant == target,
                                                    SensorDataPrediction.sensor == sensor)

    if predicted.count() == 0:
      data, saved = self.__retrieve_data(target, source, sensor)
      data = data.order_by(SensorData.created_at.asc())
      forecast = SensorDataForecast()

      information = {'plant': target, 'sensor': sensor}
      information['prediction'] = forecast.predict(information, data)
      forecast.insert_database(information)
      # print(information)

    predicted = SensorDataPrediction.select().where(SensorDataPrediction.plant == target,
                                                    SensorDataPrediction.sensor == sensor) \
                                             .order_by(SensorDataPrediction.created_at.asc()) \
                                             .limit(1)

    for sample in predicted:
      if sample.time >= datetime.datetime.now():
        released = True
        ToolChainSensor().insert_data({'sensor': sensor, 'plant': target, 'value': sample.value}, prediction=False)
        # insert hardware? -- test if DUMMYPLANT hardware?
        sample.delete_instance()
      else:
        released = False
        print('not in prediction timeframe')
    return released


if __name__ == '__main__':
  from models.sensor import Sensor
  PlantSimulate.run(Plant.get(Plant.name == 'Thomas'), Sensor.get(Sensor.name == 'temperature'))
