from IoP import app
from flask import render_template, session

@app.route('/plant/<plant>/overview')
def overview(plant):
  session['plant'] = plant
  return render_template('overview.jade', content={'current': 'overview', 'get': True})

@app.route('/plant/<plant>/<sensor>')
def sensorData(plant, sensor):
  session['plant'] = plant
  session['sensor'] = sensor
  return render_template('sensor.jade', content={'current': sensor, 'get': True})
