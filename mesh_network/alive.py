from pymongo import MongoClient
from sender import Sender
import datetime

client = MongoClient()
db = client.pot
tester = Sender()

# plantsTested = db.Plant.find({"localhost": {"$ne": True}})
# for plant in plantsTested:
  # print(plant)
now = datetime.datetime.now()
print(tester.ALIVE('192.168.178.43'))
print(datetime.datetime.now() - now)
