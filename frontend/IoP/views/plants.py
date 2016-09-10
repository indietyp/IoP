from IoP import app, init, init_overview, init_sensor, set_uuid
from flask import render_template, session
import random


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

  content = init()
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
