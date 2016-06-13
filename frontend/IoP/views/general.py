from IoP import app, init
from flask import render_template

@app.route('/')
def index():
  return render_template('main.jade')

@app.route('/sensor')
def sensorTest():
  return render_template('sensor.jade')

@app.route('/overview')
def overviewTest():
  return render_template('overview.jade', content= {'get': True})

@app.route('/plant/settings')
def plantSettingsTest():
  return render_template('plantSettings.jade')

# @app.route('/plant/marta/temperature')
# def plantSinglePageTest():
#   content = {}
#   return render_template('sensor.jade')

@app.route('/global/settings')
def globalSettingsTest():
  content = init()
  content.update({'current_active': 'Global Settings', 'type': 'setting'})
  return render_template('general/settings.jade', content=content)
