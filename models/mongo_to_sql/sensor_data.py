import pymongo
from pymongo import MongoClient
from models.sensor import SensorData, Sensor
from models.plant import Plant
from bson import ObjectId
import datetime

client = MongoClient('bilalmahmoud.de')
db = client.pot

# for asset in SensorData.select():
#   asset.delete_instance()

temperature = Sensor.get(Sensor.name == 'temperature')
humidity = Sensor.get(Sensor.name == 'humidity')
light = Sensor.get(Sensor.name == 'light')
moisture = Sensor.get(Sensor.name == 'moisture')

plant = Plant.get(Plant.name == 'marta')

i = 0
for asset in db.SensorData.find({"_id": {'$gt': ObjectId("57e954100000000000000000")}}).sort("_id", pymongo.ASCENDING):
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
    imported.sensor = sensor
    imported.plant = plant
    imported.persistant = True
    imported.created_at = datetime.datetime.fromtimestamp(asset['_id'].generation_time.timestamp())
    imported.save()

    i += 1
    if i % 100 == 0:
      print(i)

print(i)
