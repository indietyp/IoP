import pymongo
import datetime
import urllib.request

from bson import ObjectId
from pymongo import MongoClient

client = MongoClient()
db = client.pot
getData(light)

def getData(sensor):
  # plant = db.Plant.find_one({'localhost': True})['abbreviation']

  meshPlants = db.Plant.find({"localhost": {"$ne": True}})
  if meshPlants != None:
    for plant in meshPlants:
      lastentry = db.Plant.find_one({'s': sensor[0:1], 'p': plant['abbreviation']}, sort=[("_id", pymongo.DESCENDING)])
      timestamp = lastentry['_id'].getTimestamp()
      with urllib.request.urlopen('http://' + meshPlant['ip']+ ':2211/sensor/' + sensor + '/' + timestamp) as response:
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

