from IoP import app
from flask import render_template, session

@app.route('/plant/<plant>/overview')
def overview(plant):
  session['plant'] = plant
  return render_template('plant/overview.jade', content={'current': 'overview', 'get': True, 'current_active': plant, 'type': 'plant'})

@app.route('/plant/<plant>/settings')
def plantSettings(plant):
  session['plant'] = plant

  return render_template('plant/settings.jade', content={'current': 'plant_settings', 'get': True, 'current_active': plant, 'type': 'plant'})

@app.route('/plant/<plant>/<sensor>')
def sensorData(plant, sensor):
  session['plant'] = plant
  session['sensor'] = sensor
  return render_template('plant/sensor.jade', content={'current': sensor, 'get': True, 'current_active': plant, 'type': 'plant'})

