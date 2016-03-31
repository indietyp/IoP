from time import sleep
from pymongo import MongoClient

from ..driver.mcp3008 import mcp3008
from ..tools.main import Tools
from ..extensions.mailer import PlantMailer
from ..extensions.led.general import generalStatus
from ..extensions.led.moisture_bar import StatusBar
from ..extensions.waterPump import WaterPumpChecker

client = MongoClient()
db = client.pot

plantAbbreviation = db.Plant.find_one({'localhost': True})['abbreviation']

# READ SENSOR 10 TIMES
m = []
for i in range(0,10):
    m.append(mcp3008().read_pct(5))
    sleep(.2)

moisture = sum(m) / float(len(m))
if moisture != 0:

  # INSERT INTO DATABASE
  toolChain = Tools(db, plantAbbreviation)
  toolChain.insertSensor('m', round(moisture, 2))

  # ACTIVATE MAILER
  mailer = PlantMailer(plantAbbreviation, 'm')
  mailer.send()

  # INSERT IN 'led_bar'
  ledBar = StatusBar(plantAbbreviation, moisture)
  ledBar.setStatus()

  # INSERT IN WATERPUMP
  waterPump = WaterPumpChecker(plantAbbreviation)
  waterPump.set()

  # INSERT IN GENERAL LEDS
  generalMoisture = generalStatus(plantAbbreviation, 'm', moisture)
  generalMoisture.insert()

