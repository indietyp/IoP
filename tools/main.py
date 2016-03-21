from pymongo import MongoClient

class Tools:
  def __init__(self, db, plant):
    self.db = db
    self.plant = plant
  def getOptions(self, sensor):
    optimal = self.db.PlantConfig.find_one({"s": sensor,"a": self.plant['abbreviation']})['o']
    warning = self.db.PlantConfig.find_one({'s': sensor,"a": self.plant['abbreviation']})['w']
    danger = self.db.SensorType.find_one({"a": sensor})['r']

    return {'green': optimal, 'yellow': warning, 'red': danger}
  def checkOptions(self, value, dataRange):
    if dataRange['green']['min'] <= value <= dataRange['green']['max']:
      state = {'color': 'green', 'status': 'rlly no clue'}

    elif dataRange['yellow']['min'] <= value <= dataRange['yellow']['max']:
      difference = (dataRange['yellow']['max'] - dataRange['yellow']['min']) / 2
      status = 'high' if value >= (dataRange['yellow']['min'] + difference) else 'low'
      state = {'color': 'yellow', 'status': status}

    else:
      difference = (dataRange['red']['max'] - dataRange['red']['min']) / 2
      status = 'low' if value <= (dataRange['red']['min'] + difference) else 'high'
      state = {'color': 'red', 'status': status}

    return state

  def getPins(self, pinType):
    pinsRAW = self.db.ExternalDevices.find()
    pinsDone = []

    for pins in pinsRAW:
      if pinType in pins['p']:
        if isinstance( pins['p'][pinType], dict):
         for key, pin in pins['p'][pinType].items():
          if isinstance(pin, list):
            for pinInList in pin:
              pinsDone.append(int(pinInList))
          else:
            pinsDone.append(int(pin))
        elif isinstance( pins['p'][pinType], list):
          for pin in pins['p'][pinType]:
            pinsDone.append(int(pin))

    return pinsDone

  def insertSensor(self, sensor, value):
    plant = self.db.Plant.find_one({'localhost': True})['abbreviation']

    meshPlants = self.db.Plant.find({"localhost": {"$ne": True}})
    if meshPlants != None:
      for meshPlant in meshPlants:
        tmpClient = MongoClient(meshPlant['ip'])
        tmpDB = tmpClient.pot

        tmpDB.SensorData.insert_one (
          {
          'p': plant,
          's': sensor,
          'v': value
          }
        )

    self.db.SensorData.insert_one (
      {
      'p': plant,
      's': sensor,
      'v': value
      }
    )

