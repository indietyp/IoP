import json
import time
from IoP import app
from models.mesh import MeshObject
from mesh_network.daemon import MeshNetwork
from flask import render_template


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

  print(str(output))
  return json.dumps(output)
