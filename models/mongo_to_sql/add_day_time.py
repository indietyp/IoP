from models.context import DayNightTime

model = DayNightTime()
model.start = 200
model.stop = 1200

model.display = False
model.ledbar = True
model.generalleds = True
model.notification = False

model.save()
