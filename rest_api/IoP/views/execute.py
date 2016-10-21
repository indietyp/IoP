from IoP import app

import json
from mesh_network.daemon import MeshNetwork


@app.route('/execute/discover')
def execute_discover():
  MeshNetwork().discover(1)
  return json.dumps({'info': True})
