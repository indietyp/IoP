# MOVE TO TOOLS
# to tools class + administrative notices (codes)

from marrow.mailer import Message, Mailer
from pymongo import MongoClient
import pymongo
from ..tools.main import Tools
from ..tools.security import KeyChain

class PlantMailer:
  def __init__(self, plant, sensor):
    self.client = MongoClient()
    self.db = self.client.pot

    self.plant = self.db.Plant.find_one({"abbreviation": plant})
    self.sensor = sensor

  def calculate(self, dataRange, sensorData):
    toolChain = Tools(self.db, self.plant)
    times, i = (0,)*2
    end = False

    while end == False:
      checkedData = toolChain.checkOptions(sensorData[i]['v'], dataRange)
      if checkedData['color'] == 'red': # should be 'red'
        times += 1
      else:
        end = True
      i += 1

    if times % self.db.Plant.find_one({'localhost': True})['interval'] == 0:
      status = True if times != 0 else False
    else:
      status = False if times != 1 else True

    return status

  def send(self):
    toolChain = Tools(self.db, self.plant)
    sensorData = self.db.SensorData.find({'p': self.plant['abbreviation'], 's': self.sensor}).sort([('_id', pymongo.DESCENDING)])
    send = self.calculate(toolChain.getOptions(self.sensor), sensorData)

    if send == True:
      responsiblePerson = self.db.ResponsiblePerson.find_one({"person": self.plant['responsible']})
      sensorName = self.db.SensorInformation.find_one({"a": self.sensor})['gT']
      optimalRange = toolChain.getOptions(self.sensor)['green']
      keyChain = KeyChain()

      mailer = Mailer({
                  'transport.use': 'smtp',
                  'transport.host': 'smtp.gmail.com',
                  'transport.port': 465,
                  'transport.tls': 'ssl',
                  'transport.username': 'potmailer.daemon@gmail.com',
                  'transport.password': KeyChain().read('mailer'), #'x97y3bY89@',
                  'manager': {}
              })
      mailer.start()
      message = Message()
      message.author = "Plant of Things Mailer <bilalmahmoud@posteo.net>"
      message.to = responsiblePerson['person'] + " <" + responsiblePerson['email'] + ">"
      message.subject = "Pflanzennotstand! Bei Pflanze " + self.plant['name'].capitalize()
      message.plain = 'Bei der Pflanze {0} ist ein Notstand zu berichten! \n' \
                      'Bei dem Sensor {1} ist ein Wert von {2} aufgetreten \n' \
                      'Der Wert sollte eigentlich aber zwischen {3} und {4} liegen' \
                      ''.format(self.plant['name'].capitalize(), sensorName, str(sensorData[0]['v']), str(optimalRange['min']), str(optimalRange['max']))
      mailer.send(message)
      mailer.stop()

if __name__ == "__main__":
  tester = PlantMailer('m','t')
  tester.send()
