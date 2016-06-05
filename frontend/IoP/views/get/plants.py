from IoP import app
from flask import render_template, session, request

@app.route('/get/plant/overview', methods=['POST'])
def getPlant():
  plant = session['plant']
  return render_template('overview.jade', content={'get': False})

@app.route('/get/plant/sensor', methods=['POST'])
def getSensor():
  sensor = request.form['sensor']
  return render_template('sensor.jade', content={'get': False, 'current': sensor})
