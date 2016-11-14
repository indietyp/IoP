from models.plant import Plant
from models.sensor import SensorStatus, Sensor
from playhouse.shortcuts import model_to_dict
from peewee import Expression

plant = Plant.get(Plant.localhost == True)
target = Plant.get(Plant.localhost == False)


def copy_model_instace_from_localhost(target, model, *expressions):

  originals = model.select()
  for expression in expressions:
    if not isinstance(expression, Expression):
      raise ValueError('this is not exactly an expression')
    originals = originals.where(expression)

  for original in originals:
    copy = model_to_dict(original, recurse=False)

    del copy['id']
    copy['plant'] = target.id
    sql_query = model.insert(copy)
    print(sql_query.sql)
    sql_query.execute()

  return True


copy_model_instace_from_localhost(target, SensorStatus, SensorStatus.plant == plant)
# count = SensorCount.select()
# proper_sensor = Sensor.get(Sensor.name == 'humidity')
# replace = False
# for i in count:
#   if replace is True:
#     i.sensor = proper_sensor
#     i.save()
#   if i.sensor.name == 'temperature':
#     replace = True
#   print(model_to_dict(i))

#   del model_count['id']
#   model_count['plant'] = target.id

#   insert = SensorCount.insert(model_count)
