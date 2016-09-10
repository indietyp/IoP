from IoP import app
from flask import request
from pymongo import MongoClient
import json
import sys

# UPDATE
# PLANT:
# - NAME
# - RESPONSIBLE
# - RANGE
# -- GREEN
# -- YELLOW
# - LOCATION
# - TYPE
from models.plant import Plant, Person
from models.sensor import SensorSatisfactionValue, SensorSatisfactionLevel, Sensor
client = MongoClient(connect=False)
db = client.iop


@app.route('/update/plant/<p_uuid>/name', methods=['POST'])
def update_plant_name(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.name = request.form['new'].lower()
  plant.save()

  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/type', methods=['POST'])
def update_plant_type(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.species = request.form['new'].lower()
  plant.save()

  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/location', methods=['POST'])
def update_plant_location(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.location = request.form['new'].lower()
  plant.save()

  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/ranges', methods=['POST'])
def update_plant_ranges(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  sensor = Sensor.get(Sensor.name == request.form['sensor'].lower())

  level_yellow = SensorSatisfactionLevel.get(SensorSatisfactionLevel.name_color == 'yellow')
  level_green = SensorSatisfactionLevel.get(SensorSatisfactionLevel.name_color == 'green')

  value_yellow = SensorSatisfactionValue.get(SensorSatisfactionValue.plant == plant,
                                             SensorSatisfactionValue.sensor == sensor,
                                             SensorSatisfactionValue.level == level_yellow)

  value_green = SensorSatisfactionValue.get(SensorSatisfactionValue.plant == plant,
                                            SensorSatisfactionValue.sensor == sensor,
                                            SensorSatisfactionValue.level == level_green)

  value_yellow.min_value = int(request.form.getlist('data[]')[0])
  value_green.min_value = int(request.form.getlist('data[]')[1])
  value_green.max_value = int(request.form.getlist('data[]')[2])
  value_yellow.max_value = int(request.form.getlist('data[]')[3])

  value_green.save()
  value_yellow.save()

  return json.dumps({'info': 'success'})


@app.route('/update/plant/<p_uuid>/responsible', methods=['POST'])
def update_plant_responsble(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  person = Person.get(Person.email == request.form['email'], Person.name == request.form['name'])

  plant.person = person
  plant.save()
  return json.dumps({'info': 1})
