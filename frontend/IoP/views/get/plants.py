from IoP import app, init_overview, init_sensor, set_uuid, init
from flask import render_template, session, request
import urllib.request
import urllib.parse
import random
import json


@app.route('/get/plant/overview', methods=['POST'])
def getPlant():
  try:
    session['plant'] = request.form['plant']
    set_uuid()
    plant = request.form['plant']
  except Exception:
    plant = session['plant']

  content = init_overview()
  content.update({'get': False, 'current_active': plant})
  return render_template('plant/overview.jade', content=content)


@app.route('/get/plant/sensor/dataset', methods=['POST'])
def getSensorDataset():
  sensor = session['sensor']
  uuid = session['p_uuid']

  output = {}
  query = urllib.parse.urlencode({'select': 'data,prediction'})
  with urllib.request.urlopen('http://localhost:2902/plants/{}/sensor/{}?{}'.format(uuid, sensor, query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']
    output['real'] = data['data']
    output['predicted'] = data['prediction']

  return json.dumps(output)


@app.route('/get/plant/sensor/dataset/custom', methods=['POST'])
def getCustomSensorDataset():
  sensor = session['sensor']
  uuid = session['p_uuid']

  output = {}
  query = urllib.parse.urlencode({'select': 'timespan', 'start': int(request.form['latest_timestamp'])})
  with urllib.request.urlopen('http://localhost:2902/plants/{}/sensor/{}?{}'.format(uuid, sensor, query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']
    output['real'] = data['timespan']

  if len(output['real']) == 0:
    output['predicted'] = []
  else:
    query = urllib.parse.urlencode({'select': 'prediction'})
    with urllib.request.urlopen('http://localhost:2902/plants/{}/sensor/{}?{}'.format(uuid, sensor, query)) as response:
      output['predicted'] = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(output)


@app.route('/get/plant/sensor', methods=['POST'])
def getSensor():
  sensor = request.form['sensor']
  session['sensor'] = sensor
  content = {'get': False, 'current': sensor, 'random': random}
  content.update(init_sensor())
  return render_template('plant/sensor.jade', content=content)


@app.route('/get/current/plant', methods=['POST'])
def getCurrentPlant():
  return session['plant']


@app.route('/get/current/p_uuid', methods=['POST'])
def getCurrentPUUID():
  return session['p_uuid']


@app.route('/get/current/sensor', methods=['POST'])
def getCurrentSensor():
  return session['sensor']


@app.route('/get/plant/settings/data/non_specific', methods=['POST'])
def getPlantSettingsDataNonSpecific():
  uuid = session['p_uuid']

  query = urllib.parse.urlencode({'select': 'species,location'})
  with urllib.request.urlopen('http://localhost:2902/plants/{}?{}'.format(uuid, query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']
    plant_type = data['species']
    plant_location = data['location']

  return json.dumps({'type': plant_type, 'name': session['plant'], 'location': plant_location})


@app.route('/get/sensor/range', methods=['POST'])
def getSensorRange():
  query = urllib.parse.urlencode({'select': 'range'})
  with urllib.request.urlopen('http://localhost:2902/sensors/{}?{}'.format(request.form['sensor'], query)) as response:
    sensor_range = json.loads(response.read().decode('utf8'))['content']

  return json.dumps({'range': sensor_range, 'sensor': request.form['sensor']})


@app.route('/get/plant/settings/data/sensor_ranges', methods=['POST'])
def getPlantSettingsDataSensorRange():
  uuid = session['p_uuid']

  query = urllib.parse.urlencode({'select': 'range'})
  with urllib.request.urlopen('http://localhost:2902/plants/{}/sensor?{}'.format(uuid, query)) as response:
    sensor_range = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(sensor_range)


@app.route('/get/plant/settings', methods=['POST'])
def getPlantSettings():
  query = urllib.parse.urlencode({'select': 'intervals'})
  with urllib.request.urlopen('http://localhost:2902/plants/{}?{}'.format(session['p_uuid'], query)) as response:
    intervals = json.loads(response.read().decode('utf8'))['content']
  return render_template('plant/settings.jade', content={'get': False, 'current': 'settings', 'intervals': intervals})


@app.route('/get/plant/responsible', methods=['POST'])
def getPlantResponsible():
  uuid = session['p_uuid']

  query = urllib.parse.urlencode({'select': 'full'})
  with urllib.request.urlopen('http://localhost:2902/plants/{}/responsible?{}'.format(uuid, query)) as response:
    responsible = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(responsible)


@app.route('/get/responsibles', methods=['POST'])
def getResponsibles():
  query = urllib.parse.urlencode({'select': 'extensive'})
  with urllib.request.urlopen('http://localhost:2902/persons?{}'.format(query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(data)


@app.route('/get/plant/sensor/ranges', methods=['POST'])
def getPlantSensorRanges():
  uuid = session['p_uuid']
  sensor = request.form['sensor']

  query = urllib.parse.urlencode({'select': 'range'})
  with urllib.request.urlopen('http://localhost:2902/plants/{}/sensor/{}?{}'.format(uuid, sensor, query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(data)


@app.route('/update/plant/settings/non_specific', methods=['POST'])
def updateNonSpecific():
  plant = session['plant']
  uuid = session['p_uuid']
  info = 'no change'

  if request.form['name'] != session['plant']:
    data = urllib.parse.urlencode({'name': request.form['name']}).encode('ascii')
    req = urllib.request.Request('http://localhost:2902/plants/{}'.format(uuid), data)
    urllib.request.urlopen(req)

    plant = request.form['name']
    info = 'change'

  data = urllib.parse.urlencode({'species': request.form['type'], 'location': request.form['location']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/plants/{}'.format(uuid), data)
  urllib.request.urlopen(req)

  return json.dumps({'info': info, 'plant': plant})


@app.route('/update/plant/ranges', methods=['POST'])
def updateRanges():
  uuid = session['p_uuid']

  data = urllib.parse.urlencode({'ranges': True, 'sensor': request.form['sensor'], 'range[]': request.form.getlist('new[]')}, True).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/plants/{}'.format(uuid), data)
  urllib.request.urlopen(req)

  return json.dumps({'info': 'success'})


@app.route('/update/plant/responsible', methods=['POST'])
def updatePlantResponsible():
  uuid = session['p_uuid']

  data = urllib.parse.urlencode({'email': request.form['email'], 'name': request.form['name']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/plants/{}/responsible'.format(uuid), data)
  urllib.request.urlopen(req)

  return json.dumps({'info': 'success'})


@app.route('/create/responsible', methods=['POST'])
def createPlantResponsible():
  wizard = True if request.form['wizard'] == 'yes' else False
  data = urllib.parse.urlencode({'email': request.form['email'], 'name': request.form['name'], 'wizard': wizard}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/persons', data, 'PUT')
  urllib.request.urlopen(req)

  updatePlantResponsible()

  return json.dumps({'info': 'success'})


@app.route('/display/add_plant/', methods=['POST'])
def display_add_plant():
  content = init()
  content.update({'get': False, 'current_active': 'add plant'})

  return render_template('general/add.jade', content=content)


@app.route('/get/plant/sensor/data/range', methods=['POST'])
def get_plant_sensor_data_range():
  uuid = session['p_uuid']
  sensor = request.form['sensor']

  query = urllib.parse.urlencode({'select': 'data', 'start': request.form['start'], 'stop': request.form['stop']})
  with urllib.request.urlopen('http://localhost:2902/plants/{}/sensor/{}?{}'.format(uuid, sensor, query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(data)


@app.route('/get/plant/sensor/data/count', methods=['POST'])
def get_plant_data_count():
  uuid = session['p_uuid']
  sensor = request.form['sensor']

  query = urllib.parse.urlencode({'select': 'count'})
  with urllib.request.urlopen('http://localhost:2902/plants/{}/sensor/{}?{}'.format(uuid, sensor, query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(data)


@app.route('/get/plant/sensor/prediction', methods=['POST'])
def get_plant_data_prediction():
  uuid = session['p_uuid']
  sensor = request.form['sensor']

  query = urllib.parse.urlencode({'select': 'prediction'})
  with urllib.request.urlopen('http://localhost:2902/plants/{}/sensor/{}?{}'.format(uuid, sensor, query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(data)
