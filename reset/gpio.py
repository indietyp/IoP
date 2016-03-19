from pymongo import MongoClient
import RPi.GPIO as GPIO
from ..tools.main import Tools


client = MongoClient('bilalmahmoud.de', 27017)
db = client.pot
plant = db.Plant.find_one({"abbreviation": 'm'})

toolChain = Tools(db, plant)
pins = toolChain.getPins('gpio')


# set pump/lamp on
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)



