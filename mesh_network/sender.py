import socket
import time
import array
import pymongo
import datetime

from pymongo import MongoClient

class Sender:
  def __init__(self):
    self.INIT = 1
    self.MODE = {'ALIVE': 1, 'SEND': 2, 'REGISTER': 3, 'SUCCESS': 254, 'FAIL': 255}

  def summary(self, mode, data):
    data = [self.INIT, self.MODE[mode]] + data

    return data
  def send(self, data, ip):
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 4012
    sender.sendto(bytes(data), (ip, port))
    sender.close()

  def get(self):
    response = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = '127.0.0.1'
    port = 2311
    response.bind((host, port))
    response.settimeout(1)
    try:
      receivedData = response.recvfrom(1024)
      data = array.array('B')
      data.fromstring(receivedData[0])
      response.close()
    except:
      data = [255]

    return data

  def ALIVE(self, recipient):
    data = [1, 0, 0]
    data = self.summary('ALIVE', data)
    self.send(data, recipient)
    data = self.get()
    if data[0] == 255:
      ALIVE = False
      return False
    else:
      ALIVE = True
      return True

    # dbClient = MongoClient()
    # db = dbClient.pot
    # db.Plant.update_one(
    # {'ip': recipient},
    # {
    #     "$set": {
    #       'alive': ALIVE
    #     }
    # }
    # )

  def REGISTER(self, name):
    # 244.x.x.x MULTICAST ADDRESS SPACE
    host = '224.0.0.1'
    port = 4012

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.sendto(bytes([self.INIT, self.MODE['REGISTER'], 1]), (host, port))

    data = self.get()
    if data[0] == 1:
      ip = str(data[2]) + '.' + str(data[3]) + '.' + str(data[4]) + '.' + str(data[5])

      # MIRROR HOLE DATABASE!
      mainClient = MongoClient()
      mainClient.admin.command('copydb',
                            fromdb = 'pot',
                            todb = 'pot',
                            fromhost = ip)
      mainDB = mainClient.pot

      responsibleName = mainDB.ResponsiblePerson.find_one()['name']

      for val in mainDB.Plant.find():
        # UPDATE FORMER LOCAL PLANT TO FALSE
        if val['localhost'] == True:
          mainDB.Plant.update_one(
          {'localhost': True},
          {
              "$set": {
                'localhost': False,
              }
          }
          )

        # INSERT OWN PLANT IN DATABASES (want to be one of the cool guys!)
        if val['alive'] == True:
          tmpClient = MongoClient(val['ip'])
          tmpdb = tmpClient.pot
          tmpdb.Plant.insert_one(
          {
            'ip': '192.168.178.45',
            'type': 'default',
            'location': 'default',
            'responsible': responsibleName,
            'name': name.lower(),
            'abbreviation': name[0].lower(),
            'role': 'master',
            'alive': True,
            'localhost': False,
            'sensorOptima': { "green" : [], "yellow" : [  "light",  "humidity",  "moisture", "temperature" ], "red" : [ ] },
            'picture': '',
            'created_at': datetime.datetime.utcnow()
          }
          )
        tmpClient.close()


      # INSERT ITSELF IN DATABASE
      mainDB.Plant.insert_one(
      {
        'ip': '192.168.178.45',
        'type': 'default',
        'location': 'default',
        'name': name.lower(),
        'abbreviation': name[0].lower(),
        'responsible': responsibleName,
        'role': 'master',
        'alive': True,
        'localhost': True,
        'sensorOptima': { "green" : [], "yellow" : [  "light",  "humidity",  "moisture", "temperature" ], "red" : [ ] },
        'picture': '',
        'created_at': datetime.datetime.utcnow()
      }
      )

      sock.sendto(bytes([self.INIT, self.MODE['REGISTER'], 3]), (host, port))
      answer = self.get()
      if answer[2] == 100:
        # Hey Herr Wutzler! Hier bin ich
        sock.sendto(bytes([self.INIT, self.MODE['REGISTER'], self.MODE['SUCCESS']]), (host, port))
      else:
        sock.sendto(bytes([self.INIT, self.MODE['FAIL']]), (host, port))
    else:
      sock.sendto(bytes([self.INIT, self.MODE['FAIL']]), (host, port))

#tester = Sender()
# tester.REGISTER('paul')
#tester.ALIVE('192.168.178.43')
# tester.alive()

