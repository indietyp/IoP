import pymongo
from pymongo import MongoClient
from models.sensor import SensorData, Sensor
from models.plant import Plant

client = MongoClient('bilalmahmoud.de')
db = client.pot

for asset in SensorData.select():
  asset.delete_instance()

temperature = Sensor.get(Sensor.name == 'temperature')
humidity = Sensor.get(Sensor.name == 'humidity')
light = Sensor.get(Sensor.name == 'light')
moisture = Sensor.get(Sensor.name == 'moisture')

plant = Plant.get(Plant.name == 'marta')

for asset in db.SensorData.find({}).sort("_id", pymongo.ASCENDING):
  if asset['p'] == 'm':
    if asset['s'] == 't':
      sensor = temperature
    elif asset['s'] == 'h':
      sensor = humidity
    elif asset['s'] == 'l':
      sensor = light
    else:
      sensor = moisture

    imported = SensorData()
    imported.value = asset['v']
    print(imported.value)
    imported.sensor = sensor
    imported.plant = plant
    imported.persistant = True
    imported.created_at = asset['_id'].generation_time
    imported.save()
