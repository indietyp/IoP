from IoP import app
from flask import render_template, session, request
import sys

@app.route('/get/plant/overview', methods=['POST'])
def getPlant():
  try:
    session['plant'] = request.form['plant']
    plant = request.form['plant']
  except:
    print('<3', file=sys.stderr)
    plant = session['plant']

  return render_template('plant/overview.jade', content={'get': False, 'current_plant': plant})

@app.route('/get/plant/sensor', methods=['POST'])
def getSensor():
  sensor = request.form['sensor']
  return render_template('plant/sensor.jade', content={'get': False, 'current': sensor})

@app.route('/get/current/plant', methods=['POST'])
def getCurrentPlant():
  return session['plant']

@app.route('/get/plant/settings', methods=['POST'])
def getPlantSettings():
  return render_template('plant/settings.jade', content={'get': False, 'current': 'settings'})

