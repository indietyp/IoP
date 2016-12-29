import json
from IoP import app
import urllib.request
from copy import deepcopy
from flask import request
from peewee import Expression
from playhouse.shortcuts import model_to_dict
from models.plant import Person, Plant, MessagePreset, PlantNetworkUptime
from models.sensor import SensorStatus, SensorCount, SensorSatisfactionValue
from mesh_network.dedicated import MeshDedicatedDispatch


@app.route('/create/responsible', methods=['POST'])
def create_plant_name():
  person = Person()
  person.name = request.form['name']
  person.email = request.form['email']
  person.wizard = True if request.form['wizard'] == 'True' else False
  person.save()

  return json.dumps({'info': 1})


def copy_model_instance_from_localhost(target, model, *search):

  originals = model.select()
  for expression in search:
    if not isinstance(expression, Expression):
      raise ValueError('this is not exactly an expression, it\'s actually {}'.format(type(expression)))
    originals = originals.where(expression)

  for original in originals:
    copy = model_to_dict(original, recurse=False)

    del copy['id']
    copy['plant'] = target.id
    sql_query = model.insert(copy)
    print(sql_query.sql)
    sql_query.execute()

  return True


def create_plant(data):
  try:
    Plant.get(Plant.ip == data['ip'])
  except:
    plant = Plant()
    plant.name = data['name'].lower()
    plant.location = data['location']
    plant.species = data['species']
    plant.interval = data['interval']
    plant.person = Person.get(Person.email == data['email'])
    plant.ip = request.form['ip']
    plant.sat_streak = 0

    if 'uuid' in data:
      plant.uuid = data['uuid']
    if 'persistant_hold' in data:
      plant.persistant_hold = data['persistant_hold']
    if 'role' in data:
      plant.role = data['role']

    plant.save()

    local_plant = Plant.get(Plant.localhost == True)
    for model in [SensorStatus, SensorCount, SensorSatisfactionValue, PlantNetworkUptime]:
      copy_model_instance_from_localhost(plant, model, model.plant == local_plant)

    return plant


@app.route('/create/plant', methods=['POST'])
def create_plant_no_register():
  plant = create_plant(request.form)
  return json.loads({'name': plant.name, 'info': 'only created'})


@app.route('/create/plant/register', methods=['POST'])
def create_plant_register():
  plant = create_plant(request.form)
  MeshDedicatedDispatch().register(plant)
  return json.loads({'name': plant.name, 'info': 'registered'})


@app.route('/create/message', methods=['POST'])
def create_message_preset():
  data = deepcopy(request.form)
  data['heading'] = data['heading'].lower()

  for message in MessagePreset.select():
    if message.name == data['heading']:
      return {'info': 'failed, not unique'}

  msg = MessagePreset()
  msg.name = data['heading']
  msg.message = data['message']
  msg.save()

  return {'info': 'success'}
