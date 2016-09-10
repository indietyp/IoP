from models.plant import Plant

plant = Plant.get(Plant.localhost == True)
plant.ip = '192.168.178.54'
plant.save()
