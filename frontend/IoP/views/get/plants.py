from IoP import app, init_overview, init_sensor
from flask import render_template, session, request
import sys, urllib.request, urllib.parse, random, json

@app.route('/get/plant/overview', methods=['POST'])
def getPlant():
  try:
    session['plant'] = request.form['plant']
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

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + plant +'/sensor/' + sensor + '/data') as response:
    return response.read().decode('utf8')

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

@app.route('/get/plant/settings/data/non_specific', methods=['POST'])
def getPlantSettingsDataNonSpecific():
  plant = session['plant']

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + plant +'/type') as response:
    plant_type = json.loads(response.read().decode('utf8'))['data']
  with urllib.request.urlopen('http://localhost:2902/get/plant/' + plant +'/location') as response:
    plant_location = json.loads(response.read().decode('utf8'))['data']

  return json.dumps({'type': plant_type, 'name': session['plant'], 'location': plant_location})

@app.route('/get/sensor/range', methods=['POST'])
def getSensorRange():
  with urllib.request.urlopen('http://127.0.0.1:2902/get/sensor/' + request.form['sensor'] + '/range') as response:
    sensor_range = json.loads(response.read().decode('utf8'))
  return json.dumps({'range': sensor_range, 'sensor': request.form['sensor']})

@app.route('/get/plant/settings/data/sensor_ranges', methods=['POST'])
def getPlantSettingsDataSensorRange():
  plant = session['plant']

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + plant +'/sensors/range') as response:
    sensor_range = json.loads(response.read().decode('utf8'))
  return json.dumps(sensor_range)

@app.route('/get/plant/settings', methods=['POST'])
def getPlantSettings():
  return render_template('plant/settings.jade', content={'get': False, 'current': 'settings'})

@app.route('/get/plant/responsible', methods=['POST'])
def getPlantResponsible():
  plant = session['plant']

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + plant +'/responsible') as response:
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
  sensor = request.form['sensor']

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + plant + '/sensor/' + sensor + '/range') as response:
    data = json.loads(response.read().decode('utf8'))
  return json.dumps(data)

@app.route('/update/plant/settings/non_specific', methods=['POST'])
def updateNonSpecific():
  plant = session['plant']
  info = 'no change'

  if request.form['name'] != session['plant']:
    data = urllib.parse.urlencode({'new': request.form['name']}).encode('ascii')
    req = urllib.request.Request('http://localhost:2902/update/plant/' + plant + '/name', data)
    with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode('utf8'))

    plant = request.form['name']
    info = 'change'


  data = urllib.parse.urlencode({'new': request.form['type']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/plant/' + plant + '/type', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  data = urllib.parse.urlencode({'new': request.form['location']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/plant/' + plant + '/location', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  return json.dumps({'info': info, 'plant': plant})

@app.route('/update/plant/ranges', methods=['POST'])
def updateRanges():
  plant = session['plant']

  data = urllib.parse.urlencode({'sensor': request.form['sensor'], 'data[]': request.form.getlist('new[]')}, True).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/plant/' + plant + '/ranges', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  return json.dumps({'info': 'success'})

@app.route('/update/plant/responsible', methods=['POST'])
def updatePlantResponsible():
  plant = session['plant']

  data = urllib.parse.urlencode({'email': request.form['email'], 'name': request.form['name']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/plant/' + plant + '/responsible', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  return json.dumps({'info': 'success'})
