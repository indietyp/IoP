from IoP import app
from flask import request
from pymongo import MongoClient
import json, sys

# UPDATE
# PLANT:
# - NAME
# - RESPONSIBLE
# - RANGE
# -- GREEN
# -- YELLOW
# - LOCATION
# - TYPE
client = MongoClient(connect=False)
db = client.iop

@app.route('/update/plant/<plant>/name', methods=['POST'])
def update_plant_name(plant):
  result = db.Plant.update_one({'name': plant.lower()},{'$set': {'name': request.form['new'].lower()}})
  return json.dumps({'info': result.modified_count})

@app.route('/update/plant/<plant>/type', methods=['POST'])
def update_plant_type(plant):
  result = db.Plant.update_one({'name': plant.lower()},{'$set': {'type': request.form['new']}})
  return json.dumps({'info': result.modified_count})

@app.route('/update/plant/<plant>/location', methods=['POST'])
def update_plant_location(plant):
  result = db.Plant.update_one({'name': plant.lower()},{'$set': {'location': request.form['new']}})
  return json.dumps({'info': result.modified_count})

@app.route('/update/plant/<plant>/ranges', methods=['POST'])
def update_plant_ranges(plant):
  sensor = db.Sensor.find_one({'t': request.form['sensor'].lower()})['s_id']
  settings = db.Plant.find_one({'name': plant.lower()})['sensor_settings']

  for potential_setting in settings:
    if potential_setting['sensor_id'] == sensor:
      potential_setting['settings']['yellow']['min'] = int(request.form.getlist('data[]')[0])
      potential_setting['settings']['green']['min'] = int(request.form.getlist('data[]')[1])
      potential_setting['settings']['green']['max'] = int(request.form.getlist('data[]')[2])
      potential_setting['settings']['yellow']['max'] = int(request.form.getlist('data[]')[3])

  db.Plant.update_one(
    {'name': plant.lower()},
    {'$set': {'sensor_settings': settings}}
    )

  return json.dumps({'info': 'success'})

@app.route('/update/plant/<plant>/responsible', methods=['POST'])
def update_plant_responsble(plant):
  responsible_id = db.ResponsiblePerson.find_one({'username': request.form['name'], 'email': request.form['email']})['responsible_id']
  result = db.Plant.update_one({'name': plant}, {'$set': {'responsible_id': responsible_id}})

  return json.dumps({'info': result.modified_count})
