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


@app.route('/get/manage/template', methods=['POST'])
def get_manage_template():
  return render_template('general/manage.jade', content={'current_active': 'Manage', 'type': 'setting', 'get': False})


@app.route('/get/discover', methods=['POST'])
def get_device_discover():
  with urllib.request.urlopen('http://localhost:2902/execute/discover') as response:
    execute = response.read().decode('utf8')

  # MeshNetwork().discover(1)
  time.sleep(3)

  with urllib.request.urlopen('http://localhost:2902/get/discovered/0/names/extended') as response:
    output = response.read().decode('utf8')

  return output


@app.route('/get/master', methods=['POST'])
def get_master_yoda():
  with urllib.request.urlopen('http://localhost:2902/get/plants/master') as response:
    return response.read().decode('utf8')


@app.route('/create/plant', methods=['POST'])
def create_new_plant():
  data = urllib.parse.urlencode(request.form).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/create/plant/register', data)
  with urllib.request.urlopen(req) as response:
    data = response.read().decode('utf8')

  return data


@app.route('/get/day_night', methods=['POST'])
def get_day_night():
  with urllib.request.urlopen('http://localhost:2902/get/day/night/time') as response:
    output = json.loads(response.read().decode('utf8'))

  return json.dumps(output[0])


@app.route('/change/day_night', methods=['POST'])
def change_day_night():
  data = urllib.parse.urlencode(request.form).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/day/night/time', data)
  with urllib.request.urlopen(req) as response:
    data = response.read().decode('utf8')

  return data


@app.route('/get/manage', methods=['POST'])
def get_manage():
  with urllib.request.urlopen('http://localhost:2902/get/plants/name/extended') as response:
    output = response.read().decode('utf8')

  return output


@app.route('/update/plant/toggle', methods=['POST'])
def update_plant_toggle():
  from mesh_network.dedicated import MeshDedicatedDispatch

  target = Plant.get(uuid=request.form['uuid'])
  mode = 'deactivate' if target.active else 'active'
  MeshDedicatedDispatch().remove(mode, target)

  return json.dumps(True)


@app.route('/update/plant/purge', methods=['POST'])
def update_plant_purge():
  from mesh_network.dedicated import MeshDedicatedDispatch

  target = Plant.get(uuid=request.form['uuid'])
  MeshDedicatedDispatch().remove('remove', target)

  return json.dumps(True)


@app.route('/update/slave/master', methods=['POST'])
def update_slave_master():
  from mesh_network.dedicated import MeshDedicatedDispatch
  from models.plant import Plant

  slave = Plant.get(uuid=request.form['slave'])
  local = Plant.get(localhost=True)

  if request.form['target'] == slave.role:
    return json.dumps(False)

  target = Plant.get(uuid=request.form['target'])

  if slave.role == str(local.uuid):
    MeshDedicatedDispatch().slave_update(1, {'uuid': target.uuid, 'ip': target.ip}, slave)

  slave.role = str(target.uuid)
  slave.save()
  MeshDedicatedDispatch().update('slave host change', slave.uuid, target=target)

  return json.dumps(True)
