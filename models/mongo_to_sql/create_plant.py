from models.plant import Plant, Person

plant = Plant()
plant.name = 'Holger'
plant.location = 'space'
plant.species = 'rose'
plant.interval = 7

plant.person = Person.get(Person.wizard == True)
plant.ip = '192.168.178.65'

plant.sat_streak = 0
plant.save()
print(str(plant.uuid))
