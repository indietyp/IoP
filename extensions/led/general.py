from pymongo import MongoClient
import pymongo
import RPi.GPIO as GPIO
from ...tools.main import Tools

class generalStatus():
  """docstring for setStatus"""
  def __init__(self, plant, sensor, value):
    self.client = MongoClient()
    self.db = self.client.pot
    self.plant = self.db.Plant.find_one({"abbreviation": plant})

    self.sensor = self.db.SensorType.find_one({"a": sensor})
    self.sensorName = self.sensor['t']
    self.sensorAbbreviation = sensor
    self.value = value

  def calculate(self, currentState, state):
    stateOfSensor = ''
    if self.sensorName in currentState['green']:
      stateOfSensor = 'green'
    if self.sensorName in currentState['yellow']:
      stateOfSensor = 'yellow'
    if self.sensorName in currentState['red']:
      stateOfSensor = 'red'
    if state != currentState:
      currentState[stateOfSensor].remove(self.sensorName)
      currentState[state['color']].append(self.sensorName)

    return currentState
  def insert(self):
    toolChain = Tools(self.db, self.plant)
    dataRange = toolChain.getOptions(self.sensorAbbreviation)
    state = toolChain.checkOptions(self.value, dataRange)
    newState = self.calculate(self.plant['sensorOptima'], state)
    self.db.Plant.update_one(
    {"abbreviation": self.plant['abbreviation']},
    {
        "$set": {
          'sensorOptima': newState
        }
    }
    )

  def set(self):
    red = False
    yellow = False
    green = False

    currentStates = self.plant['sensorOptima']

    if currentStates['red']:
      red = True
    elif currentStates['yellow']:
      yellow = True
    else: green = True

    leds = self.db.ExternalDevices.find_one({'n': 'generalLEDs'})

    toolChain = Tools(self.db, self.plant)
    gpioPins = toolChain.getPins('gpio')

    gpioPins = [5, 6, 13]

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    for pin in gpioPins:
      GPIO.setup(pin, GPIO.OUT)


    #with leds['p']['gpio'] as led:
    GPIO.output(13, True)
    # GPIO.output(leds['p']['gpio']['green'], False)
    # GPIO.output(leds['p']['gpio']['yellow'], False)
    # GPIO.output(leds['p']['gpio']['red'], False)

    # GPIO.output(leds['p']['gpio']['green'], green)
    # GPIO.output(leds['p']['gpio']['yellow'], yellow)
    # GPIO.output(leds['p']['gpio']['red'], red)

    def full(self):
      self.insert()
      self.set()

if __name__ == "__main__":
  test = generalStatus('m', 'l', 50)
  test.set()
