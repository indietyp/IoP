import json
import time
from IoP import app
from models.plant import Plant
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
  data = urllib.parse.urlencode({'execute': True}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/discover', data)
  urllib.request.urlopen(req)

  time.sleep(1)

  query = urllib.parse.urlencode({'select': 'extensive'})
  with urllib.request.urlopen('http://127.0.0.1:2902/discover?{}'.format(query)) as response:
    output = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(output)


@app.route('/get/master', methods=['POST'])
def get_master_yoda():
  query = urllib.parse.urlencode({'select': 'master'})
  with urllib.request.urlopen('http://localhost:2902/plants?{}'.format(query)) as response:
    output = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(output)


@app.route('/create/plant', methods=['POST'])
def create_new_plant():
  data = dict(request.form)
  data['register'] = True
  data = urllib.parse.urlencode(data).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/plants', data, 'PUT')
  with urllib.request.urlopen(req) as response:
    data = response.read().decode('utf8')

  return data


@app.route('/get/day_night', methods=['POST'])
def get_day_night():
  query = urllib.parse.urlencode({'select': 'full'})
  with urllib.request.urlopen('http://localhost:2902/daynight?{}'.format(query)) as response:
    output = json.loads(response.read().decode('utf8'))['content'][0]

  return json.dumps(output)


@app.route('/change/day_night', methods=['POST'])
def change_day_night():
  data = urllib.parse.urlencode(request.form).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/daynight', data)
  urllib.request.urlopen(req)

  return json.dumps(True)


@app.route('/get/manage', methods=['POST'])
def get_manage():
  query = urllib.parse.urlencode({'select': 'extensive'})
  with urllib.request.urlopen('http://localhost:2902/plants?{}'.format(query)) as response:
    output = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(output)


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
