from models.plant import Plant, Person
from models.mesh import MeshMessage
from playhouse.shortcuts import model_to_dict

plant = Plant()
plant.name = 'marta'
plant.location = 'table'
plant.species = 'tulpe'
plant.interval = 6

plant.person = Person.get(Person.wizard == True)
plant.ip = '192.168.178.54'
plant.uuid = '91c9280b76c142a393eb85250065230f'
plant.localhost = True
# plant.id = 1

plant.sat_streak = 0
plant.save()
print(str(plant.uuid))
