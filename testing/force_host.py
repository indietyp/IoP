from models.plant import Plant
for plant in list(Plant.select().where(Plant.host == True)):
  plant.host = False
  plant.save()


target = Plant.get(name='marta')
target.host = True
target.save()
