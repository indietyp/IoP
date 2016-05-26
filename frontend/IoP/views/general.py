from IoP import app
from flask import render_template

@app.route('/')
def index():
    return render_template('main.jade')

@app.route('/sensor')
def sensorTest():
  return render_template('sensor.jade')

@app.route('/overview')
def overviewTest():
    return render_template('overview.jade')

@app.route('/plant/settings')
def plantSettingsTest():
    return render_template('plantSettings.jade')
