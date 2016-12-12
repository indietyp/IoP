from models.plant import Plant
from models.sensor import SensorData, SensorDataPrediction
from tools.forecast import SensorDataForecast
from mesh_network.dedicated import MeshDedicatedDispatch
import random
import datetime


# class SimulatePlant():
#   def __init__(self, plant, sensor):
#     self.plant = plant
#     self.sensor = sensor

#     data = SensorData.select().where(SensorData.plant == plant,
#                                      SensorData.sensor == sensor)

#     if data.count() < 1:
#       self.__copy(sensor)

#   def __copy(self, sensor):
#     plant_sensor_data = {}
#     for plant in Plant.select():
#       data = SensorData.select().where(SensorData.plant == plant,
#                                        SensorData.sensor == sensor)

#       plant_sensor_data[plant.name] = data.count

#     largest = sorted(plant_sensor_data)[0]

#     # simulated plant -> copy to plant and then proceed
#     # new timestamps! c:

#   def run(self):
#     # see if in table -> create new? or use old?
#     #  -> if 0 -> run regression again!
#     # grab earliest -> put into database and delete from table
#     # call MeshNetworkDispatch
#     pass

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
      print(type(sample.time))
      new = SensorData()
      new.plant = target
      new.sensor = sensor
      new.value = predicted.value
      new.created_at = sample.time
      new.save()

      sample.delete_instance()

    MeshDedicatedDispatch().new_data(sensor)

    return True
