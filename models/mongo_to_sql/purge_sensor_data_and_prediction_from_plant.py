from models.plant import Plant
from models.sensor import SensorData, SensorDataPrediction

target = Plant.get(Plant.name == 'Thomas')
target.name = 'thomas'
target.save()

SensorData.delete().where(SensorData.plant == target).execute()
SensorDataPrediction.delete().where(SensorDataPrediction.plant == target).execute()
