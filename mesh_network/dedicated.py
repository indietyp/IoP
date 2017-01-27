import sys
import socket
import logging
import tools.logger
import urllib.request
from copy import deepcopy
from models.plant import Plant
from tools.main import VariousTools
from mesh_network.daemon import MeshNetwork
from playhouse.shortcuts import model_to_dict
logger = logging.getLogger('mesh')


class MeshDedicatedDispatch(object):
  def __init__(self):
    pass

  def get(self, timeout):
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = '127.0.0.1'
    port = 2311
    receiver.bind((host, port))
    receiver.settimeout(timeout)
    # data mode is not considered right now, but built in
    # because builtin is better than if I ever wanted to use it, and it's not
    try:
      data = receiver.recvfrom(1024)
      data = data[0].decode('utf-8')
      data = eval(data)
      data = data[1]
    except:
      data = 254

    return data

  def alive(self):
    from models.plant import Plant
    from models.plant import PlantNetworkStatus
    from models.plant import PlantNetworkUptime

    daemon = MeshNetwork()
    online = PlantNetworkStatus.select().where(PlantNetworkStatus.name == 'online')
    offline = PlantNetworkStatus.select().where(PlantNetworkStatus.name == 'offline')

    masters = Plant.select().where(Plant.localhost == False, Plant.role == 'master')
    masters = list(masters)
    plants = deepcopy(masters)

    local = Plant.get(localhost=True)
    slaves = Plant.select().where(Plant.localhost == False, Plant.role == str(local.uuid))
    plants.extend(list(slaves))

    for plant in plants:
      daemon.alive(plant, 1)
      status = self.get(5)

      online_dataset = None
      offline_dataset = None

      options = [[online, online_dataset, [1]],
                 [offline, offline_dataset, [254, 255]]]

      for i in options:
        i[1] = None
        i[1], _ = PlantNetworkUptime.get_or_create(plant=plant,
                                                   status=i[0],
                                                   defaults={'overall': 0, 'current': 0})

        if status in i[2]:
          i[1].current += 1
          i[1].overall += 1
          i[1].save()

          if plant.role != 'master':
            data = urllib.parse.urlencode({}).encode('ascii')

            for master in masters:
              req = urllib.request.Request('http://{}:2902/update/plant/{}/alive/{}/add'.format(master.ip, str(plant.uuid), i[1].status.name), data)
              try:
                with urllib.request.urlopen(req) as response:
                  response.read().decode('utf8')
              except Exception as e:
                logger.warning('{} - {}: {}'.format(plant.name, master.name, e))

        for dataset in options:
          if dataset[0] != i[0] and i[1].current != 0:
            i[1].current = 0
            i[1].save()

  def register(self, plant):
    from models.mesh import MeshObject
    daemon = MeshNetwork()
    successful = False

    # transmit data to other plants
    if plant.role == 'master':
      daemon.register(1, origin=plant)
      status = self.get(120)

      if status == 1:
        obj = MeshObject.get(MeshObject.ip == plant.ip)
        obj.registered = True
        obj.save()

        successful = True
      else:
        raise BaseException('something went from: error code: ' + str(status))
    else:
      master = Plant.get(Plant.uuid == plant.role)
      daemon.register_lite(mode=1, target=plant, plant=master)
      status = self.get(120)

      if status == 1:
        obj = MeshObject.get(MeshObject.ip == plant.ip)
        obj.registered = True
        obj.save()

        successful = True

    if successful:
      dict_plant = model_to_dict(plant)
      dict_plant['email'] = plant.person.email
      del dict_plant['id']
      del dict_plant['person']

      for rest in Plant.select().where(Plant.ip != plant.ip, Plant.localhost == False, Plant.role == 'master'):
        data = urllib.parse.urlencode(dict_plant).encode('ascii')
        req = urllib.request.Request('http://' + rest.ip + ':2902/create/plant', data)
        try:
          with urllib.request.urlopen(req) as response:
            response.read().decode('utf8')
        except Exception as e:
          print(e)

  def new_data(self, sensor):
    from models.plant import Plant

    daemon = MeshNetwork()
    for plant in Plant.select().where(Plant.localhost == False, Plant.role == 'master'):
      daemon.deliver(1, sub=1, recipient=plant, sensor=sensor)

  def reboot(self):
    """ for system reboot """
    from models.plant import Plant
    daemon = MeshNetwork()

    for plant in Plant.select().where(Plant.localhost == False):
      daemon.deliver(2, sub=1, recipient=plant)

    return True

  def update(self, name, uuid):
    from models.plant import Plant
    if name.lower() == 'plant':
      counter = 0
    elif name.lower() == 'sensor':
      counter = 1
    elif name.lower() == 'person':
      counter = 2
    elif name.lower() == 'satisfaction':
      counter = 3
    elif name.lower() == 'message':
      counter = 4
    elif name.lower() == 'host':
      counter = 5
    else:
      return False

    daemon = MeshNetwork()

    for plant in Plant.select().where(Plant.localhost == False):
      daemon.deliver(3, sub=1, recipient=plant, message=[counter, str(uuid)])

    return True

  def slave_data(self, plant, sensor):
    # currently only supported : moisture, nothing probably following
    if sensor.name == 'moisture':
      daemon = MeshNetwork()
      daemon.slave(mode=1, target=plant, sensor=sensor)

      return True
    else:
      return False

if __name__ == '__main__':
  logger = logging.getLogger('mesh')
  if VariousTools.verify_database():
    if len(sys.argv) < 2:
      logger.info('executed standard action - reboot')
      MeshDedicatedDispatch().reboot()
    elif sys.argv[1] == 'alive':
      logger.info('executed argument action - alive')
      MeshDedicatedDispatch().alive()
    elif sys.argv[1] == 'reboot':
      logger.info('executed argument action - reboot')
      MeshDedicatedDispatch().reboot()
    elif len(sys.argv) == 3 and sys.argv[1] == 'testing' and sys.argv[2] == 'register':
      logger.info('executed argument action - register - testing')
      from models.plant import Plant
      plant = Plant.get(Plant.name == 'Thomas')
      logger.info(plant.ip)
      MeshDedicatedDispatch().register(plant)
    elif len(sys.argv) == 4 and sys.argv[1] == 'testing' and sys.argv[2] == 'slave' and sys.argv[3] == 'register':
      logger.info('executed argument action - register - testing')
      from models.plant import Plant
      plant = Plant.get(Plant.name == 'gertrud')
      MeshDedicatedDispatch().register(plant)
  else:
    logger.info('aborted action - database required - no database provided')
