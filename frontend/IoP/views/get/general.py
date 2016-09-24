import json
import time
from IoP import app
from models.mesh import MeshObject
from models.plant import Plant, Person
from mesh_network.daemon import MeshNetwork
from mesh_network.dedicated import MeshDedicatedDispatch
from flask import render_template, request


@app.route('/get/general/settings', methods=['POST'])
def getGeneralSettings():
  return render_template('general/settings.jade', content={'current_active': 'Global Settings', 'type': 'setting', 'get': False})


# no mesh rest integration -> problematic!
@app.route('/get/discover', methods=['POST'])
def get_device_discover():
  MeshNetwork().discover(1)
  time.sleep(3)

  output = []
  for item in MeshObject.select().where(MeshObject.registered == False):
    output.append(item.ip)

  return json.dumps(output)


@app.route('/create/plant', methods=['POST'])
def create_new_plant():
  try:
    Plant.get(Plant.ip == request.form['ip'])
  except:
    plant = Plant()
    plant.name = request.form['name']
    plant.location = request.form['location']
    plant.species = request.form['species']
    plant.interval = request.form['interval']

    plant.person = Person.get(Person.email == request.form['email'])
    plant.ip = request.form['ip']
    plant.sat_streak = 0
    plant.save()

    MeshDedicatedDispatch().register(plant)

  return str(True)
