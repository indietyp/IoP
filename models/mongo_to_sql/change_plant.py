from models.plant import Plant
plant = Plant.get(Plant.localhost == True)
plant.ip = '192.168.178.43'
plant.save()
