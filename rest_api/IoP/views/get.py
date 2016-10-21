from IoP import app

import sys
import datetime
import json
from uuid import UUID
from bson import json_util
from playhouse.shortcuts import model_to_dict

from models.mesh import MeshObject
from models.plant import Plant, PlantNetworkUptime, Person, MessagePreset
from models.sensor import Sensor, SensorData, SensorCount, SensorSatisfactionValue, SensorDataPrediction


# the frontend is dumb! only give data from database, scripts to the other stuff
@app.route('/get/plants/name')
def get_plants_name():
  plants = []
  for plant in Plant.select():
    plants.append([str(plant.uuid), plant.name])
  return json.dumps(plants)


@app.route('/get/plant/<p_uuid>')
def get_hole_plant(p_uuid):
  plant = model_to_dict(Plant.get(Plant.uuid == p_uuid))
  del plant['id']
  plant['uuid'] = str(plant['uuid'])
  return json.dumps(plant, default=json_util.default)


@app.route('/get/plant/<p_uuid>/sensor/<s_uuid>/latest')
def get_latest_dataset(p_uuid, s_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  sensor = Sensor.get(Sensor.name == s_uuid)

  sd = SensorData.select().where(SensorData.plant == plant) \
                          .where(SensorData.sensor == sensor) \
                          .order_by(SensorData.created_at.desc())

  selected = model_to_dict(sd[0])
  del selected['sensor']
  del selected['plant']
  del selected['id']

  return json.dumps(selected, default=json_util.default)


@app.route('/get/plant/<p_uuid>/created_at')
def get_created_at(p_uuid):
  created_at = Plant.get(Plant.uuid == UUID(p_uuid)).created_at
  return json.dumps(created_at, default=json_util.default)


@app.route('/get/plant/<p_uuid>/type')
def get_plant_type(p_uuid):
  species = Plant.get(Plant.uuid == UUID(p_uuid)).species
  return json.dumps({'data': species})


@app.route('/get/plant/<p_uuid>/location')
def get_plant_location(p_uuid):
  location = Plant.get(Plant.uuid == UUID(p_uuid)).location
  return json.dumps({'data': location})


@app.route('/get/plant/<plant>/current_status')
def get_plant_status(plant):
  # 'status': 'green', 'counter': 2
  # 1..4 = 1, 5..8: 2, 9..-: 3
  pass


@app.route('/get/plant/<plant>/average_status/percent')
def get_plant_average_status(plant):
  pass


@app.route('/get/plant/<p_uuid>/survived')
def get_survived(p_uuid):
  difference = datetime.datetime.now() - Plant.get(Plant.uuid == UUID(p_uuid)).created_at
  difference = float(difference.days + round((difference.seconds // 3600) / 24, 1))
  return json.dumps({'data': difference})


@app.route('/get/plant/<p_uuid>/responsible')
def get_responsible_full_dataset(p_uuid):
  responsible = Plant.get(Plant.uuid == UUID(p_uuid)).person
  responsible = model_to_dict(responsible)
  del responsible['id']
  del responsible['preset']

  return json.dumps(responsible)


@app.route('/get/plant/<p_uuid>/responsible/username')
def get_responsible_username(p_uuid):
  dataset = json.loads(get_responsible_full_dataset(p_uuid))
  return json.dumps({'username': dataset['name']})


@app.route('/get/plant/<p_uuid>/responsible/email')
def get_responsible_email(p_uuid):
  dataset = json.loads(get_responsible_full_dataset(p_uuid))
  return json.dumps({'email': dataset['email']})


@app.route('/get/plant/<p_uuid>/responsible/wizard')
def get_responsible_wizard(p_uuid):
  dataset = json.loads(get_responsible_full_dataset(p_uuid))
  return json.dumps({'wizard': dataset['wizard']})


# @app.route('/get/plant/<p_uuid>/location')
# def get_location(plant):
#   return json.dumps(db.Plant.find_one({'name': plant})['location'], default=json_util.default)


@app.route('/get/plant/<p_uuid>/sensor/<sensor>/prediction')
def get_plant_sensor_prediction(p_uuid, sensor):
  plant = Plant.get(Plant.uuid == p_uuid)
  sensor = Sensor.get(Sensor.name == sensor)

  sensor_prediction_set = SensorDataPrediction.select() \
                                              .where(SensorDataPrediction.plant == plant) \
                                              .where(SensorDataPrediction.sensor == sensor) \
                                              .order_by(SensorDataPrediction.created_at.asc())

  output = []
  for prediction in sensor_prediction_set:
    prediction = model_to_dict(prediction)

    prediction['timestamp'] = prediction['time'].timestamp()

    del prediction['id']
    del prediction['plant']
    del prediction['sensor']

    prediction['created_at'] = str(prediction['created_at'])
    prediction['time'] = str(prediction['time'])

    output.append(prediction)

  return json.dumps(output)


@app.route('/get/plant/<p_uuid>/sensor/<sensor>/data')
def get_plant_sensor_data(p_uuid, sensor):
  plant = Plant.get(Plant.uuid == p_uuid)
  sensor = Sensor.get(Sensor.name == sensor)
  sensor_data_set = SensorData.select() \
                              .where(SensorData.plant == plant) \
                              .where(SensorData.sensor == sensor) \
                              .order_by(SensorData.created_at.asc())

  content = []
  for data in sensor_data_set:
    data = model_to_dict(data)
    try:
      data['timestamp'] = data['created_at'].replace('+00:00', '')
      data['timestamp'] = datetime.datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
    except:
      data['timestamp'] = datetime.datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
    data['timestamp'] = data['timestamp'].timestamp()

    del data['id']
    del data['plant']
    del data['sensor']
    content.append(data)
  return json.dumps(content)


@app.route('/get/plant/<p_uuid>/sensor/<sensor>/data/<float:until>')
def get_plant_sensor_data_after(p_uuid, sensor, until):
  sensor = Sensor.get(Sensor.name == sensor)
  plant = Plant.get(Plant.uuid == p_uuid)

  date_time = datetime.datetime.fromtimestamp(until + 1)
  sensor_data_set = SensorData.select() \
                              .where(SensorData.plant == plant) \
                              .where(SensorData.sensor == sensor) \
                              .where(SensorData.created_at > date_time) \
                              .order_by(SensorData.created_at.asc())

  content = []
  for data in sensor_data_set:
    data = model_to_dict(data)
    try:
      data['timestamp'] = data['created_at'].replace('+00:00', '')
      data['timestamp'] = datetime.datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
    except:
      data['timestamp'] = datetime.datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
    data['timestamp'] = data['timestamp'].timestamp()

    del data['id']
    del data['plant']
    del data['sensor']
    content.append(data)
  return json.dumps(content)


@app.route('/get/plant/<p_uuid>/sensor/<sensor>/data/current')
def get_plant_current_sensor_data(p_uuid, sensor):
  plant = Plant.get(Plant.uuid == p_uuid)
  sensor = Sensor.get(Sensor.name == sensor)
  latest = SensorData.select() \
                     .where(SensorData.plant == plant) \
                     .where(SensorData.sensor == sensor) \
                     .order_by(SensorData.created_at.desc())[0]

  latest = model_to_dict(latest)
  del latest['id']
  del latest['plant']
  del latest['sensor']

  return json.dumps(latest)


@app.route('/get/plant/<p_uuid>/sensor/<sensor>/range')
def get_plant_sensor_range(p_uuid, sensor):
  sensor = Sensor.get(Sensor.name == sensor)
  plant = Plant.get(Plant.uuid == p_uuid)

  ranges = SensorSatisfactionValue.select() \
                                  .where(SensorSatisfactionValue.plant == plant) \
                                  .where(SensorSatisfactionValue.sensor == sensor)

  output = {}
  for spectrum in ranges:
    output[spectrum.level.name_color] = {'max': spectrum.max_value, 'min': spectrum.min_value}
    if spectrum.level.name_color == 'red':
      output[spectrum.level.name_color] = {'max': sensor.max_value, 'min': sensor.min_value}

  return json.dumps(output)


def get_sensor_data_high_low(p_uuid, sensor, high, date_time=None):
  plant = Plant.get(Plant.uuid == p_uuid)
  sensor = Sensor.get(Sensor.name == sensor)
  # sensor_id = db.Sensor.find_one({'t': sensor})['s_id']
  mode = SensorData.created_at.asc() if high is False else SensorData.created_at.desc()

  sensor_data_set = SensorData.select() \
                              .where(SensorData.plant == plant) \
                              .where(SensorData.sensor == sensor) \
                              .order_by(mode)

  if date_time is not None:
    sensor_data_set = SensorData.select() \
                                .where(SensorData.plant == plant) \
                                .where(SensorData.sensor == sensor) \
                                .where(SensorData.created_at >= date_time) \
                                .order_by(mode)

  if sensor_data_set.count() == 0:
    return None

  raw = sensor_data_set[0]
  data = model_to_dict(raw)
  data['t'] = data['created_at'].replace('+00:00', '')
  try:
    data['t'] = datetime.datetime.strptime(data['t'], '%Y-%m-%d %H:%M:%S')
  except:
    data['t'] = datetime.datetime.strptime(data['t'], "%Y-%m-%d %H:%M:%S.%f")
  data['t'] = data['t'].timestamp()

  data['v'] = data['value']

  del data['created_at']
  del data['value']
  del data['id']
  del data['plant']
  del data['sensor']

  return data


@app.route('/get/plant/<p_uuid>/sensor/<sensor>/<any(high,low):mode>/ever')
def get_plant_sensor_data_high_ever(sensor, p_uuid, mode):
  stuff = True if mode == 'high' else False
  return json.dumps(get_sensor_data_high_low(p_uuid, sensor, stuff))


@app.route('/get/plant/<p_uuid>/sensor/<sensor>/<any(high, low):mode>/today/<any(yes,no):if_no_data_days_before>')
def get_plant_sensor_data_high_today(sensor, p_uuid, mode, if_no_data_days_before):
  stuff = True if mode == 'high' else False
  today = datetime.date.today()
  dateToDatetime = datetime.datetime.combine(today, datetime.time())
  if if_no_data_days_before == 'yes':
    data = None
    while data is None:
      data = get_sensor_data_high_low(p_uuid, sensor, stuff, dateToDatetime)
      dateToDatetime = dateToDatetime - datetime.timedelta(days=1)
  elif if_no_data_days_before == 'no':
    data = get_sensor_data_high_low(p_uuid, sensor, stuff, dateToDatetime)

  return json.dumps(data)


# @app.route('/get/sensor/<sensor>/range/min')
# @app.route('/get/sensor/<sensor>/range/max')
@app.route('/get/sensor/<sensor>/range')
def get_sensor_range(sensor):
  sensor = Sensor.get(Sensor.name == sensor)
  return json.dumps({'max': sensor.max_value, 'min': sensor.min_value})


@app.route('/get/sensor/<sensor>/unit')
def get_sensor_unit(sensor):
  sensor = Sensor.get(Sensor.name == sensor)
  return json.dumps({'unit': sensor.unit})


@app.route('/get/plant/<p_uuid>/status/average')
def get_sensor_status_average_percent(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  c = Sensor.select().count()
  sensor_count = SensorCount.select() \
                            .where(SensorCount.plant == plant)

  average = {'red': 0, 'yellow': 0, 'green': 0}

  for count in sensor_count:
    average[count.level.name_color] += count.count

  summary = 0
  for key, item in average.items():
    average[key] /= c
    summary += average[key]

  print(summary, file=sys.stdout)
  output = {}
  for key, item in average.items():
    try:
      output[key] = [round(item / summary * 100), item]
    except ZeroDivisionError:
      output[key] = [0, item]

  return json.dumps(output)


@app.route('/get/plant/<p_uuid>/status/online/')
def get_sensor_staus_online(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)

  uptimes = PlantNetworkUptime.select() \
                              .where(PlantNetworkUptime.plant == plant)

  output = {}
  summary = 0

  for uptime in uptimes:
    output[uptime.status.name] = [0, uptime.overall, uptime.current]
    summary += uptime.overall

  for key, uptime in output.items():
    print(type(output[key][1]))
    output[key][0] = round(output[key][1] / summary * 100) if output[key][1] != 0 else 0

  if output == {}:
    output = {'online': [0, 0.0, 0.0], 'offline': [0, 0.0, 0.0]}

  return json.dumps(output)


@app.route('/get/plant/<p_uuid>/sensors/range')
def get_plant_sensors_range(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  sensors = Sensor.select()

  output = []
  for sensor in sensors:
    ranges = SensorSatisfactionValue.select() \
                                    .where(SensorSatisfactionValue.plant == plant) \
                                    .where(SensorSatisfactionValue.sensor == sensor)

    tmp = {}
    for spectrum in ranges:
      tmp[spectrum.level.name_color] = {'max': spectrum.max_value, 'min': spectrum.min_value}
      if spectrum.level.name_color == 'red':
        tmp[spectrum.level.name_color] = {'max': sensor.max_value, 'min': sensor.min_value}
    output.append({'settings': tmp, 'sensor': sensor.name})

  return json.dumps(output)


@app.route('/get/responsible/persons')
def get_responsible_persons():
  people = Person.select()
  # people = db.ResponsiblePerson.find()

  output = []
  for person in people:
    dict_person = model_to_dict(person)
    del dict_person['id']
    del dict_person['preset']
    output.append(dict_person)

  return json.dumps(output)


@app.route('/get/plant/<p_uuid>/sensor/<sensor>/data/start/<int:start>/stop/<int:stop>')
def get_plant_data_selective(p_uuid, sensor, start, stop):
  plant = Plant.get(Plant.uuid == p_uuid)
  sensor = Sensor.get(Sensor.name == sensor)
  sensor_data_set = SensorData.select() \
                              .where(SensorData.plant == plant) \
                              .where(SensorData.sensor == sensor) \
                              .order_by(SensorData.created_at.desc()) \
                              .offset(start) \
                              .limit(stop - start)


  content = []
  for data in sensor_data_set:
    data = model_to_dict(data)
    try:
      data['timestamp'] = data['created_at'].replace('+00:00', '')
      data['timestamp'] = datetime.datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
    except:
      data['timestamp'] = datetime.datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
    data['timestamp'] = data['timestamp'].timestamp()

    del data['id']
    del data['plant']
    del data['sensor']
    content.append(data)
  return json.dumps(content)


@app.route('/get/plant/<p_uuid>/sensor/<sensor>/data/count')
def get_plant_count(p_uuid, sensor):
  plant = Plant.get(Plant.uuid == p_uuid)
  sensor = Sensor.get(Sensor.name == sensor)
  sensor_data_set = SensorData.select() \
                              .where(SensorData.plant == plant) \
                              .where(SensorData.sensor == sensor)

  return json.dumps({'count': sensor_data_set.count()})


@app.route('/get/messages/names')
def get_message_names():
  messages = MessagePreset.select()

  output = []
  for message in messages:
    output.append({'name': message.name, 'uuid': str(message.uuid)})

  return json.dumps(output)


@app.route('/get/message/<m_uuid>/content')
def get_message_content(m_uuid):
  message = MessagePreset.get(MessagePreset.uuid == m_uuid)
  return json.dumps(message.message)


@app.route('/get/discovered/<int:registered>/names')
def get_current_discover(registered):
  if registered == 0:
    items = MeshObject.select().where(MeshObject.registered == False)
  elif registered == 1:
    items = MeshObject.select().where(MeshObject.registered == True)
  elif registered == 2:
    items = MeshObject.select()
  else:
    return json.dumps({'info': 'path registered value not valid'})

  output = []
  for item in items:
    output.append(item.ip)

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
