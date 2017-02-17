from models.plant import Plant
target = Plant.get(localhost=True)
target.save()
