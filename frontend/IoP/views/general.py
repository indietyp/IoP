from IoP import app
from flask import render_template

@app.route('/')
def index():
  content = {}
  return render_template('main.jade')

@app.route('/sensor')
def sensorTest():
  content = {}
  return render_template('sensor.jade')

@app.route('/overview')
def overviewTest():
  content = {}
  return render_template('overview.jade', content= {'get': True})

@app.route('/plant/settings')
def plantSettingsTest():
  content = {}
  return render_template('plantSettings.jade')

# @app.route('/plant/marta/temperature')
# def plantSinglePageTest():
#   content = {}
#   return render_template('sensor.jade')

@app.route('/global/settings')
def globalSettingsTest():
  content = {}
  return render_template('globalSettings.jade')
