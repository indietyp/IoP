import socket
from mesh_network.daemon import MeshNetwork


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
    # because built in is better than if I ever wanted to use it, and it's not
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
    offline = PlantNetworkStatus.select().where(PlantNetworkStatus.name == 'online')

    for plant in Plant.select().where(Plant.localhost == False):
      daemon.alive(plant, 5)
      status = self.get(5)

      online_dataset = None
      offline_dataset = None

      options = [[online, online_dataset, [1]],
                 [offline, offline_dataset, [254, 255]]]

      for i in options:
        i[1] = PlantNetworkUptime.get_or_create(PlantNetworkUptime.plant == plant,
                                                PlantNetworkUptime.status == i[0],
                                                defaults={'overall': 0, 'current': 0})

        if status in i[2]:
          i[1].current += 1
          i[1].overall += 1
          i[1].save()

        for dataset in options:
          if dataset[0] != i[0] and i[1].current != 0:
            i[1].current = 0
            i[1].save()

  def register(self, plant):
    from models.mesh import MeshObject

    # transmit data to other plants
    daemon = MeshNetwork()
    daemon.register(1, origin=plant)
    status = self.get(120)

    if status == 1:
      obj = MeshObject.get(MeshObject.ip == plant.ip)
      obj.registered = True
      obj.save()
    else:
      raise BaseException('something went from: error code: ' + str(status))

  def new_data(self, sensor):
    from models.plant import Plant

    daemon = MeshNetwork()
    for plant in Plant.select().where(Plant.localhost == False):
      daemon.deliver(1, sub=1, recipient=plant, sensor=sensor)

  def reboot(self):
    """ for system reboot """
    from models.plant import Plant
    daemon = MeshNetwork()

    for plant in Plant.select().where(Plant.localhost == False):
      daemon.deliver(2, sub=1, recipient=plant)
