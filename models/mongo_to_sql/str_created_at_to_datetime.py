from models.sensor import SensorData
import datetime

count = SensorData.select().count()
i = 0
j = 0
for data in SensorData.select():
  if isinstance(data.created_at, str):
    try:
      data.created_at = data.created_at.replace('+00:00', '')
      data.created_at = datetime.datetime.strptime(data.created_at, '%Y-%m-%d %H:%M:%S')
    except:
      data.created_at = datetime.datetime.strptime(data.created_at, "%Y-%m-%d %H:%M:%S.%f")
    i += 1
    data.save()

  j += 1
  if j % 1000 == 0:
    print('done: {}%'.format(round(j / count * 100, 2)))
  if i % 1000 == 0:
    print('processed: {}'.format(i))
print('-------------------')
print('done: {}%'.format(round(j / count * 100, 2)))
print('processed: {}'.format(i))
