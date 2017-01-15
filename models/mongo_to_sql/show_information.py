from models.plant import Plant

for plant in Plant.select():
  print(plant.name)
