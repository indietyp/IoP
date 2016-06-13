from IoP import app
from pymongo import MongoClient
from bson import json_util
import json, datetime, bson, random, pymongo

client = MongoClient(connect=False)
db = client.iop

# the frontend is dumb! only give data from database, scripts to the other stuff
@app.route('/get/plants/name')
def get_plants_name():
  plants = []
  for plant in db.Plant.find():
    plants.append([plant['plant_id'], plant['name']])
  return json.dumps(plants)

@app.route('/get/plant/<plant>/created_at')
def get_created_at(plant):
  return json.dumps(db.Plant.find_one({'name': plant})['created_at'], default=json_util.default)

@app.route('/get/plant/<plant>/survived')
def get_survived(plant):
  difference = datetime.datetime.now() - db.Plant.find_one({'name': plant})['created_at']
  return json.dumps(float(difference.days))

@app.route('/get/plant/<plant>/responsible')
def get_responsible_full_dataset(plant):
  responsible_id = db.Plant.find_one({'name': plant})['responsible_id']
  responsible_dataset = db.ResponsiblePerson.find_one({'responsible_id': responsible_id})
  del responsible_dataset['_id']
  del responsible_dataset['responsible_id']
  return json.dumps(responsible_dataset)

@app.route('/get/plant/<plant>/responsible/username')
def get_responsible_username(plant):
  dataset = json.loads(get_responsible_full_dataset(plant))
  return json.dumps(dataset['person'])

@app.route('/get/plant/<plant>/responsible/email')
def get_responsible_email(plant):
  dataset = json.loads(get_responsible_full_dataset(plant))
  return json.dumps(dataset['email'])

@app.route('/get/plant/<plant>/responsible/wizard')
def get_responsible_wizard(plant):
  dataset = json.loads(get_responsible_full_dataset(plant))
  return json.dumps(dataset['wizard'])

@app.route('/get/plant/<plant>/location')
def get_location(plant):
  return json.dumps(db.Plant.find_one({'name': plant})['location'], default=json_util.default)

@app.route('/get/plant/<plant>/sensor/<sensor>/data')
def get_plant_sensor_data(plant, sensor):
  plant_id = db.Plant.find_one({'name': plant})['plant_id']
  sensor_id = db.Sensor.find_one({'t': sensor})['s_id']
  sensorData = db.SensorData.find({'p': plant_id, 's': sensor_id})
  content = []
  for data in sensorData:
    content.append({'v': data['v'], 'dt': data['_id'].generation_time.timestamp()})
  return json.dumps(content)

@app.route('/get/plant/<plant>/sensor/<sensor>/current')
def get_plant_current_sensor_data(plant, sensor):
  plant_id = db.Plant.find_one({'name': plant})['plant_id']
  sensor_id = db.Sensor.find_one({'t': sensor})['s_id']
  newestData = db.SensorData.find_one({'s': sensor_id, 'p': plant_id}, sort=[("_id", pymongo.DESCENDING)])
  del newestData['_id']
  del newestData['p']
  del newestData['s']
  return json.dumps(newestData)
# @app.route('/get/plants/random')

# @app.route('/get/plant/name')
# @app.route('/get/plant/created_at')
# @app.route('/get/plant/location')
# @app.route('/get/plant/sensor/data')
# @app.route('/get/plant/sensor/data/forecast')
# @app.route('/get/plant/sensor/data/current')
# @app.route('/get/plant/sensor/<sensor>/high/today')
# @app.route('/get/plant/sensor/<sensor>/difference/today')
# @app.route('/get/plant/sensor/<sensor>/low/today')

# @app.route('/get/plant/sensor/<sensor>/high/ever')
# @app.route('/get/plant/sensor/<sensor>/difference/ever')
# @app.route('/get/plant/sensor/<sensor>/low/ever')

# @app.route('/get/plant/sensors/overall')
# @app.route('/get/plant/online') # TRUE if online FALSE if online time!
# @app.route('/get/plant/responsible')

# @app.route('/get/responsible/<responsible>/wizard') # get TRUE or FALSE
# @app.route('/get/responsible/wizard')
