import pymongo
import json
import time
import datetime

from flask import Flask
from pymongo import MongoClient
from bson import ObjectId
app = Flask(__name__)

client = MongoClient('bilalmahmoud.de')
db = client.pot

@app.route('/')
def index():
  return 'no REST-API here!'

@app.route('/sensor', defaults={'timestamp': None, 'sensor': None})
@app.route('/sensor/<sensor>', defaults={'timestamp': None})
@app.route('/sensor/<sensor>/<int:timestamp>')
def sensor(sensor,timestamp):
  # SEARCHING FOR LATEST RECORDS
  results = []
  if timestamp != None:
    query = {'_id': {'$gt': ObjectId(format(timestamp, 'x') + '0000000000000000')}, 's': sensor}
  else:
    if sensor == None:
      query = {}
    else:
      query = {'s': sensor}

  for x in db.SensorData.find(query):
    results.append(x)

  return JSONEncoder().encode(results)

@app.route('/plant', defaults={'plant': None})
@app.route('/plant/<plant>')
def plant(plant):
  results = []
  if plant != None:
    query = {'name': plant}
  else:
    query = {}

  for x in db.Plant.find(query):
    # x.pop('_id') (_id is needed for verification)
    x['created_at'] = x['created_at'].timestamp()
    results.append(x)

  return JSONEncoder().encode(results)

@app.route('/config/plant/<plant>')
def plantConfig(plant):
  results = []
  for x in db.PlantConfig.find({'a': plant[0:1]}):
    # x.pop('_id') (_id is needed for verification)
    results.append(x)

  return JSONEncoder().encode(results)

@app.route('/config/person', defaults={'email': None})
@app.route('/config/person/<email>')
def responsiblePerson(email):
  results = []
  if sensor != None:
    query = {'email': email}
  else:
    query = {}
  for x in db.ResponsiblePerson.find(query):
    results.append(x)

  return JSONEncoder().encode(results)

@app.route('/config/sensor/type', defaults={'sensor': None})
@app.route('/config/sensor/type/<sensor>')
def sensorType(sensor):
  results = []
  if sensor != None:
    query = {'a': sensor[0:1]}
  else:
    query = {}

  for x in db.SensorType.find(query):
    results.append(x)

  return JSONEncoder().encode(results)

@app.route('/config/external', defaults={'device': None})
@app.route('/config/external/<device>')
def externalDevices(device):
  results = []
  print(device)
  if sensor != None:
    query = {'n': device}
  else:
    query = {}

  for x in db.ExternalDevices.find(query):
    results.append(x)

  return JSONEncoder().encode(results)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

if __name__ == '__main__':
    app.run(debug= True)

# thanks to Gary Maynard, who helped me a lot to create this REST-API
