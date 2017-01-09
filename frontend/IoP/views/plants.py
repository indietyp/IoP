import os
import json
import random
import urllib.request
from flask import render_template, session
from IoP import app, init, init_overview, init_sensor, set_uuid, request


@app.route('/plant/<plant>')
@app.route('/plant/<plant>/overview')
def overview(plant):
  session['plant'] = plant
  set_uuid()

  content = init()
  content.update(init_overview())
  content.update({'current': 'overview', 'get': True, 'current_active': plant, 'type': 'plant'})
  return render_template('plant/overview.jade', content=content)


@app.route('/plant/<plant>/settings')
def plantSettings(plant):
  session['plant'] = plant
  set_uuid()

  with urllib.request.urlopen('http://localhost:2902/get/plant/' + session['p_uuid'] + '/intervals') as response:
    intervals = json.loads(response.read().decode('utf8'))
  print(intervals)

  content = init()
  content['intervals'] = intervals
  content.update({'current': 'plant_settings', 'get': True, 'current_active': plant, 'type': 'plant'})
  return render_template('plant/settings.jade', content=content)


@app.route('/plant/<plant>/<sensor>')
def sensorData(plant, sensor):
  session['plant'] = plant
  session['sensor'] = sensor
  set_uuid()

  content = init()
  content.update(init_sensor())
  content.update({'current': sensor, 'get': True, 'current_active': plant, 'type': 'plant', 'random': random})
  return render_template('plant/sensor.jade', content=content)


@app.route('/upload/picture/plant', methods=['POST'])
def upload_picture_plant():
  image = request.files['profile-image']
  destination = os.path.dirname(os.path.realpath(__file__)) + '/../static/images/plant/'
  extension = image.filename.split('.')[1]

  if not os.path.exists(destination):
    os.makedirs(destination)

  for file in os.listdir(destination):
    if file.split('.')[0] == session['p_uuid']:
      os.remove(os.path.join(destination, file))

  image.save('{}{}.{}'.format(destination, session['p_uuid'], extension))
  return 'success'
