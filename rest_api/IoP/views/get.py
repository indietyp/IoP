from IoP import app
from pymongo import MongoClient
from bson import json_util, ObjectId
import json, datetime, bson, random, pymongo
import sys

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

@app.route('/get/plant/<plant>/type')
def get_plant_type(plant):
  return json.dumps({'data': db.Plant.find_one({'name': plant})['type']})

@app.route('/get/plant/<plant>/location')
def get_plant_location(plant):
  return json.dumps({'data': db.Plant.find_one({'name': plant})['location']})

@app.route('/get/plant/<plant>/current_status')
def get_plant_status(plant):
  # 'status': 'green', 'counter': 2
  # 1..4 = 1, 5..8: 2, 9..-: 3
  pass

@app.route('/get/plant/<plant>/average_status/percent')
def get_plant_average_status(plant):
  pass

@app.route('/get/plant/<plant>/survived')
def get_survived(plant):
  difference = datetime.datetime.now() - db.Plant.find_one({'name': plant})['created_at']
  return json.dumps(float(difference.days + round((difference.seconds//3600)/24, 1)))

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

@app.route('/get/plant/<plant>/sensor/<sensor>/data/current')
def get_plant_current_sensor_data(plant, sensor):
  plant_id = db.Plant.find_one({'name': plant})['plant_id']
  sensor_id = db.Sensor.find_one({'t': sensor})['s_id']
  newestData = db.SensorData.find_one({'s': sensor_id, 'p': plant_id}, sort=[("_id", pymongo.DESCENDING)])
  del newestData['_id']
  del newestData['p']
  del newestData['s']
  return json.dumps(newestData)

@app.route('/get/plant/<plant>/sensor/<sensor>/range')
def get_plant_sensor_range(plant, sensor):
  sensor_id = db.Sensor.find_one({'t': sensor})['s_id']
  for ranges in db.Plant.find_one({'name': plant})['sensor_settings']:
    if ranges['sensor_id'] == sensor_id:
      return json.dumps(ranges['settings'])

def get_sensor_data_high_low(plant, sensor, high, timestamp=None):
  plant_id = db.Plant.find_one({'name': plant})['plant_id']
  sensor_id = db.Sensor.find_one({'t': sensor})['s_id']
  mode = pymongo.ASCENDING if high == False else pymongo.DESCENDING

  fillter = {'s': sensor_id, 'p': plant_id}
  if timestamp != None:
    fillter.update({'_id': {'$gt': ObjectId(format(int(timestamp), 'x') + '0000000000000000')}})

  data = db.SensorData.find_one(fillter, sort=[("v", mode)])
  try:
    data['t'] = data['_id'].generation_time.timestamp()
    del data['_id']
    del data['p']
    del data['s']
  except:
    pass
  return data

@app.route('/get/plant/<plant>/sensor/<sensor>/<any(high,low):mode>/ever')
def get_plant_sensor_data_high_ever(sensor, plant, mode):
  stuff = True if mode == 'high' else False
  return json.dumps(get_sensor_data_high_low(plant, sensor, stuff))

@app.route('/get/plant/<plant>/sensor/<sensor>/<any(high, low):mode>/today/<any(yes,no):if_no_data_days_before>')
def get_plant_sensor_data_high_today(sensor, plant, mode, if_no_data_days_before):
  stuff = True if mode == 'high' else False
  today = datetime.date.today()
  dateToDatetime = datetime.datetime.combine(today, datetime.time())
  if if_no_data_days_before == 'yes':
    data = None
    while data == None:
      timestamp = dateToDatetime.timestamp()
      data = get_sensor_data_high_low(plant, sensor, stuff, timestamp)
      dateToDatetime = dateToDatetime - datetime.timedelta(days=1)
  elif if_no_data_days_before == 'no':
    timestamp = dateToDatetime.timestamp()
    data = get_sensor_data_high_low(plant, sensor, stuff, timestamp)
  return json.dumps(data)

# @app.route('/get/sensor/<sensor>/range/min')
# @app.route('/get/sensor/<sensor>/range/max')
@app.route('/get/sensor/<sensor>/range')
def get_sensor_range(sensor):
  return json.dumps(db.Sensor.find_one({'t': sensor})['r'])

@app.route('/get/sensor/<sensor>/unit')
def get_sensor_unit(sensor):
  return json.dumps({'unit': db.Sensor.find_one({'t': sensor})['u']})

@app.route('/get/plant/<plant>/status/average')
def get_sensor_status_average_percent(plant):
  plant = db.Plant.find_one({'name': plant})
  average = {'red': 0, 'yellow': 0, 'green': 0}
  sensor_counter = 0
  for key, item in plant['sensor_status'][1]['overall_counter'].items():
    for key_s, item_s in average.items():
      average[key_s] += item[key_s]
    sensor_counter += 1

  summary = 0
  for key, item in average.items():
    average[key] /= sensor_counter
    summary += average[key]

  print(summary, file=sys.stdout)
  output = {}
  for key, item in average.items():
    output[key] = [round(item / summary * 100), item]

  return json.dumps(output)

@app.route('/get/plant/<plant>/status/online/')
def get_sensor_staus_online(plant):
  plant = db.Plant.find_one({'name': plant})
  online = plant['online'][1]
  offline = plant['offline'][1]
  summary = online + offline
  return json.dumps({'online': [round(online / summary * 100), online], 'offline': [round(offline / summary * 100), offline]})

@app.route('/get/plant/<plant>/sensors/range')
def get_plant_sensors_range(plant):
  ranges = db.Plant.find_one({'name': plant})['sensor_settings']

  for item in ranges:
    item['sensor'] = db.Sensor.find_one({'s_id': item['sensor_id']})['t']
    del item['sensor_id']

  return json.dumps(ranges)

@app.route('/get/responsible/persons')
def get_responsible_persons():
  people = db.ResponsiblePerson.find()

  output = []
  for person in people:
    output.append({'name': person['username'], 'email': person['email'], 'wizard': person['wizard']})

  return json.dumps(output)


# @app.route('/get/plants/random')

# @app.route('/get/plant/name') - ---
# @app.route('/get/plant/created_at') - done
# @app.route('/get/plant/location') - done
# @app.route('/get/plant/sensor/data') - done
# @app.route('/get/plant/sensor/data/forecast')
# @app.route('/get/plant/sensor/data/current') -- done
# @app.route('/get/plant/sensor/<sensor>/high/today') - done (modified)
# @app.route('/get/plant/sensor/<sensor>/difference/today') - ---
# @app.route('/get/plant/sensor/<sensor>/low/today') - done (modified)

# @app.route('/get/plant/sensor/<sensor>/high/ever') - done
# @app.route('/get/plant/sensor/<sensor>/difference/ever') - ---
# @app.route('/get/plant/sensor/<sensor>/low/ever') - done

# @app.route('/get/plant/sensors/overall') - done (path modified)
# @app.route('/get/plant/online') # TRUE if online FALSE if online time!
# @app.route('/get/plant/responsible') - done

# @app.route('/get/responsible/<responsible>/wizard') # get TRUE or FALSE - done
# @app.route('/get/responsible/wizard')
