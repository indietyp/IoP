# TODO alive_script
# as daemon -> also roudup and self

from pymongo import MongoClient
from sender import Sender
import datetime
from functools import reduce

client = MongoClient()
db = client.pot
tester = Sender()

# plantsTested = db.Plant.find({"localhost": {"$ne": True}})
# for plant in plantsTested:
  # print(plant)
i = 0
j = 0
ival = []
jval = []
while True:
	j += 1
	if tester.ALIVE('192.168.178.43') == False:
		jval.append(j)
		i += 1
		ival.append(i)
		print('--------------')
		print(reduce(lambda x, y: x + y, jval) / len(jval))
		print('--')
		#print(len(jval))
		print(j)
		print('--')
		print(reduce(lambda x, y: x + y, ival) / len(ival))
		print('--')
		print(i)
		#print('--')
		j = 0
	#now = datetime.datetime.now()
	#print(tester.ALIVE('192.168.178.43'))
	#print(datetime.datetime.now() - now)
