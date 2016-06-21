from IoP import app
from flask import request
from pymongo import MongoClient
import json

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
