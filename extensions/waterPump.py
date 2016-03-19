import pymongo
from pymongo import MongoClient
from ..tools.main import Tools
from ..driver.mcp3008 import mcp3008
import RPi.GPIO as GPIO
import time


class WaterPumpChecker:
  def __init__(self, plant):
    self.client = MongoClient()
    self.db = self.client.pot
    self.plant = self.db.Plant.find_one({"abbreviation": plant})

    self.tools = Tools(self.db, self.plant)
  def calculate(self, sensorData):
    now = sensorData[0]
    before = sensorData[1]
    dataRange = self.tools.getOptions('m')
    state = self.tools.checkOptions(now['v'], dataRange)

    status = False
    if state['color'] == 'red':
      if before['v'] - now['v'] <= 3 and not before['v'] - now['v'] < 0:
        status = True

    return status
  def set(self):
    sensorData = self.db.SensorData.find({'p': self.plant['abbreviation'], 's': 'm'}).sort([('_id', pymongo.DESCENDING)])
    status = self.calculate(sensorData)

    if status == True:
      pins = self.tools.getPins('gpio')
      pinPump = self.db.ExternalDevices.find_one({'n': 'waterPump'})['p']['gpio'][0]

      # set pump/lamp on
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BCM)
      for pin in pins:
        GPIO.setup(pin, GPIO.OUT)

      GPIO.output(pinPump, True)
      yet = round(time.time(), 0)
      while (round(time.time(), 0) - yet) <= 120:
        m = []
        for i in range(0,10):
          m.append(mcp3008().read_pct(5))
          time.sleep(1)
        status = self.tools.checkOptions((sum(m) / float(len(m))), self.tools.getOptions('m'))
        if status['color'] == 'green':
          break
      GPIO.output(pinPump, False)

if __name__ == "__main__":
  tester = WaterPumpChecker('m')
  tester.set()
