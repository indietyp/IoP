import json
from models.sensor import SensorData
from playhouse.shortcuts import model_to_dict
from peewee import Expression, Clause, fn, SQL


def get_sensor_data_high_low(plant, sensor, configuration, target=None):
  mode = SensorData.created_at.asc() if configuration is False else SensorData.created_at.desc()

  dataset = SensorData.select(SensorData.value.alias('v'),
                              fn.CAST(Clause(fn.strftime('%s', SensorData.created_at), SQL('AS INT'))).alias('t')) \
                      .where(SensorData.plant == plant) \
                      .where(SensorData.sensor == sensor) \
                      .order_by(mode)

  if target is not None:
    dataset = dataset.where(SensorData.created_at >= target)

  dataset = dataset.limit(1).dicts()

  if dataset.count() == 0:
    return None

  data = list(dataset)[0]
  return data


def copy_model_instance_from_localhost(target, model, *search):

  originals = model.select()
  for expression in search:
    if not isinstance(expression, Expression):
      raise ValueError('this is not exactly an expression, it\'s actually {}'.format(type(expression)))
    originals = originals.where(expression)

  for original in originals:
    copy = model_to_dict(original, recurse=False)

    del copy['id']
    copy['plant'] = target.id
    sql_query = model.insert(copy)
    print(sql_query.sql)
    sql_query.execute()

  return True


def time_request_from_converter(data):
  seconds = 0
  if 'seconds' in data:
    seconds += int(data['seconds'])

  if 'minutes' in data:
    seconds += int(data['minutes']) * 60

  if 'hours' in data:
    seconds += int(data['hours']) * 60 * 60

  if 'days' in data:
    seconds += int(data['days']) * 24 * 60 * 60

  minutes = seconds / 60
  hours = minutes / 60

  return seconds, minutes, hours


def data_formatting(code=200, data=[]):
  return json.dumps({'code': code, 'content': data})
