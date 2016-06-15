from IoP import app, init_overview, init_sensor
from flask import render_template, session, request
import sys, urllib.request, random

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

@app.route('/get/plant/settings', methods=['POST'])
def getPlantSettings():
  return render_template('plant/settings.jade', content={'get': False, 'current': 'settings'})
