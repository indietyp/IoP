from pymongo import MongoClient
from sender import Sender

client = MongoClient()
db = client.pot
tester = Sender()

plantsTested = db.Plant.find({"localhost": {"$ne": True}})
for plant in plantsTested:
  print(plant)
  tester.ALIVE(plant['ip'])

