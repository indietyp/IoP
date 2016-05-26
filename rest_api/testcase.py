import pymongo
import datetime
import urllib.request
import json

from bson import ObjectId
from pymongo import MongoClient

client = MongoClient()
db = client.pot

def getData(sensor):
  meshPlants = db.Plant.find({"localhost": {'$ne': True}})
  if meshPlants != None:
    for plant in meshPlants:
      lastentry = db.SensorData.find_one({'s': sensor[0:1], 'p': plant['abbreviation']}, sort=[("_id", pymongo.DESCENDING)])
      timestamp = round(lastentry['_id'].generation_time.timestamp())
      timestamp += 1

      with urllib.request.urlopen('http://' + plant['ip']+ ':2211/sensor/' + sensor + '/' + str(timestamp)) as response:
         rawJSON = response.read()
         for field in json.loads(rawJSON):
          field['_id'] = ObjectId(field['_id'])
          db.SensorData.insert_one(field)

getData('light')
