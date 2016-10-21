from models.plant import Plant
from models.sensor import SensorData
from tools.forecast import SensorDataForecast


class SimulatePlant():
  def __init__(self, plant, sensor):
    self.plant = plant
    self.sensor = sensor

    data = SensorData.select().where(SensorData.plant == plant,
                                     SensorData.sensor == sensor)

    if data.count() < 1:
      self.__copy(sensor)

  def __copy(self, sensor):
    plant_sensor_data = {}
    for plant in Plant.select():
      data = SensorData.select().where(SensorData.plant == plant,
                                       SensorData.sensor == sensor)

      plant_sensor_data[plant.name] = data.count

    largest = sorted(plant_sensor_data)[0]

    # simulated plant -> copy to plant and then proceed
    # new timestamps! c:

  def run(self):
    # see if in table -> create new? or use old?
    #  -> if 0 -> run regression again!
    # grab earliest -> put into database and delete from table
    # call MeshNetworkDispatch
    pass
