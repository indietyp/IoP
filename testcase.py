import pymongo
import datetime
import urllib.request

from bson import ObjectId
from pymongo import MongoClient

client = MongoClient()
db = client.pot

def getData(sensor):
  # plant = db.Plant.find_one({'localhost': True})['abbreviation']

  meshPlants = db.Plant.find({"localhost": {'$ne': True}})
  if meshPlants != None:
    for plant in meshPlants:
      lastentry = db.SensorData.find_one({'s': sensor[0:1], 'p': plant['abbreviation']}, sort=[("_id", pymongo.DESCENDING)])
      timestamp = round(lastentry['_id'].generation_time.timestamp())
      timestamp += 1
      print(timestamp)
      with urllib.request.urlopen('http://' + plant['ip']+ ':2211/sensor/' + sensor[0:1] + '/' + str(timestamp)) as response:
         html = response.read()
         print(html)


  #     tmpClient = MongoClient(meshPlant['ip'])
  #     tmpDB = tmpClient.pot

  #     tmpDB.SensorData.insert_one (
  #       {
  #       'p': plant,
  #       's': sensor,
  #       'v': value
  #       }
  #     )

  # self.db.SensorData.insert_one (
  #   {
  #   'p': plant,
  #   's': sensor,
  #   'v': value
  #   }
  # )

getData('light')