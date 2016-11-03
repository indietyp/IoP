import json
import time
from IoP import app
from models.mesh import MeshObject
from models.plant import Plant, Person
from mesh_network.daemon import MeshNetwork
# from mesh_network.dedicated import MeshDedicatedDispatch
from flask import render_template, request
import urllib.request
import urllib.parse


@app.route('/get/general/settings', methods=['POST'])
def getGeneralSettings():
  return render_template('general/settings.jade', content={'current_active': 'Global Settings', 'type': 'setting', 'get': False})


# no mesh rest integration -> problematic!
@app.route('/get/discover', methods=['POST'])
def get_device_discover():
  with urllib.request.urlopen('http://localhost:2902/execute/discover') as response:
    execute = response.read().decode('utf8')

  # MeshNetwork().discover(1)
  time.sleep(3)

  with urllib.request.urlopen('http://localhost:2902/get/discovered/0/names') as response:
    output = response.read().decode('utf8')

  return output


@app.route('/create/plant', methods=['POST'])
def create_new_plant():
  data = urllib.parse.urlencode(request.form).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/create/plant/register', data)
  with urllib.request.urlopen(req) as response:
    data = response.read().decode('utf8')

  return data
