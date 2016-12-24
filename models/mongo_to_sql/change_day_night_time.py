from models.context import DayNightTime

for dnt in DayNightTime.select():
  dnt.stop = '2300'
  dnt.save()
