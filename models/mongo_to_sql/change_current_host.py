from models.plant import Plant

plant = Plant.get(Plant.localhost == True)
plant.host = True
plant.save()
