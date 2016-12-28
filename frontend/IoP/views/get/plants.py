from IoP import app, init_overview, init_sensor, set_uuid, init
from flask import render_template, session, request
import sys
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
  except:
    print('<3', file=sys.stderr)
    plant = session['plant']

  # content = {}
  content = init_overview()
  content.update({'get': False, 'current_active': plant})
  return render_template('plant/overview.jade', content=content)


@app.route('/get/plant/sensor/dataset', methods=['POST'])
def getSensorDataset():
  sensor = session['sensor']
  plant = session['plant']
  uuid = session['p_uuid']

  output = {}
  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/sensor/' + sensor + '/data') as response:
    output['real'] = json.loads(response.read().decode('utf8'))

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/sensor/' + sensor + '/prediction') as response:
    output['predicted'] = json.loads(response.read().decode('utf8'))

  return json.dumps(output)


@app.route('/get/plant/sensor/dataset/custom', methods=['POST'])
def getCustomSensorDataset():
  sensor = session['sensor']
  uuid = session['p_uuid']

  output = {}
  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/sensor/' + sensor + '/data/' + str(float(request.form['latest_timestamp']))) as response:
    output['real'] = json.loads(response.read().decode('utf8'))

  if len(output['real']) == 0:
    output['predicted'] = []
  else:
    with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/sensor/' + sensor + '/prediction') as response:
      output['predicted'] = json.loads(response.read().decode('utf8'))

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

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/type') as response:
    plant_type = json.loads(response.read().decode('utf8'))['data']
  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/location') as response:
    plant_location = json.loads(response.read().decode('utf8'))['data']

  return json.dumps({'type': plant_type, 'name': session['plant'], 'location': plant_location})


@app.route('/get/sensor/range', methods=['POST'])
def getSensorRange():
  with urllib.request.urlopen('http://127.0.0.1:2902/get/sensor/' + request.form['sensor'] + '/range') as response:
    sensor_range = json.loads(response.read().decode('utf8'))
  return json.dumps({'range': sensor_range, 'sensor': request.form['sensor']})


@app.route('/get/plant/settings/data/sensor_ranges', methods=['POST'])
def getPlantSettingsDataSensorRange():
  uuid = session['p_uuid']

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/sensors/range') as response:
    sensor_range = json.loads(response.read().decode('utf8'))
  return json.dumps(sensor_range)


@app.route('/get/plant/settings', methods=['POST'])
def getPlantSettings():
  with urllib.request.urlopen('http://localhost:2902/get/plant/' + session['p_uuid'] + '/intervals') as response:
    intervals = json.loads(response.read().decode('utf8'))
  return render_template('plant/settings.jade', content={'get': False, 'current': 'settings', 'intervals': intervals})


@app.route('/get/plant/responsible', methods=['POST'])
def getPlantResponsible():
  plant = session['plant']
  uuid = session['p_uuid']

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/responsible') as response:
    responsible = json.loads(response.read().decode('utf8'))
  return json.dumps(responsible)


@app.route('/get/responsibles', methods=['POST'])
def getResponsibles():
  with urllib.request.urlopen('http://localhost:2902/get/responsible/persons') as response:
    data = json.loads(response.read().decode('utf8'))
  return json.dumps(data)


@app.route('/get/plant/sensor/ranges', methods=['POST'])
def getPlantSensorRanges():
  plant = session['plant']
  uuid = session['p_uuid']
  sensor = request.form['sensor']

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/sensor/' + sensor + '/range') as response:
    data = json.loads(response.read().decode('utf8'))
  return json.dumps(data)


@app.route('/update/plant/settings/non_specific', methods=['POST'])
def updateNonSpecific():
  plant = session['plant']
  uuid = session['p_uuid']
  info = 'no change'

  if request.form['name'] != session['plant']:
    data = urllib.parse.urlencode({'new': request.form['name']}).encode('ascii')
    req = urllib.request.Request('http://localhost:2902/update/plant/' + uuid + '/name', data)
    with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode('utf8'))

    plant = request.form['name']
    info = 'change'

  data = urllib.parse.urlencode({'new': request.form['type']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/plant/' + uuid + '/type', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  data = urllib.parse.urlencode({'new': request.form['location']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/plant/' + uuid + '/location', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  return json.dumps({'info': info, 'plant': plant})


@app.route('/update/plant/ranges', methods=['POST'])
def updateRanges():
  uuid = session['p_uuid']

  data = urllib.parse.urlencode({'sensor': request.form['sensor'], 'data[]': request.form.getlist('new[]')}, True).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/plant/' + uuid + '/ranges', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  return json.dumps({'info': 'success'})


@app.route('/update/plant/responsible', methods=['POST'])
def updatePlantResponsible():
  uuid = session['p_uuid']

  data = urllib.parse.urlencode({'email': request.form['email'], 'name': request.form['name']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/plant/' + uuid + '/responsible', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  return json.dumps({'info': 'success'})


@app.route('/create/responsible', methods=['POST'])
def createPlantResponsible():
  wizard = True if request.form['wizard'] == 'yes' else False
  data = urllib.parse.urlencode({'email': request.form['email'], 'name': request.form['name'], 'wizard': wizard}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/create/responsible', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  data = urllib.parse.urlencode({'email': request.form['email'], 'name': request.form['name']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/plant/' + uuid + '/responsible', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

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

  with urllib.request.urlopen('http://localhost:2902/get/plant/' +
                              uuid + '/sensor/' + sensor + '/data/start/' +
                              request.form['start'] + '/stop/' + request.form['stop']) as response:
    data = response.read().decode('utf8')
  return data


@app.route('/get/plant/sensor/data/count', methods=['POST'])
def get_plant_data_count():
  uuid = session['p_uuid']
  sensor = request.form['sensor']

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/sensor/' + sensor + '/data/count') as response:
    data = response.read().decode('utf8')
  return data


@app.route('/get/plant/sensor/prediction', methods=['POST'])
def get_plant_data_prediction():
  uuid = session['p_uuid']
  sensor = request.form['sensor']

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + uuid + '/sensor/' + sensor + '/prediction') as response:
    output = response.read().decode('utf8')

  return output
