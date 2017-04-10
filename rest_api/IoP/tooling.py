import json
from flask import make_response, request
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
  converted = json.dumps({'code': code, 'content': data})

  response = make_response(converted)
  response.mimetype = 'application/json'
  return response


def get_data(*args, **kwargs):
  # required: {'name': STR, 'type': TYPE, 'fallback': STUFF, 'restricted': [STR, {'name': STR, 'fallback': STR}], 'list': BOOLEAN}
  # restrictive: BOOLEAN
  # hardmode: BOOLEAN
  required = kwargs['required'] if 'required' in kwargs and isinstance(kwargs['required'], list) else []
  restrictive = kwargs['restrictive'] if 'restrictive' in kwargs else False
  hardmode = kwargs['hardmode'] if 'hardmode' in kwargs else False

  if isinstance(required, dict):
    required = [required]

  code = 200
  data = {}

  data.update(request.args)
  data.update(request.form)
  if request.is_json:
    data.update(request.get_json())

  for fragment in data:
    if isinstance(fragment, str):
      fragment = fragment.lower()

  for req in required:
    if 'fallback' not in req:
      if req['type'] == bool:
        req['fallback'] = False
      elif req['type'] == str:
        req['fallback'] = ''
      elif req['type'] == int:
        req['fallback'] = 0
      elif req['type'] == float:
        req['fallback'] = 0.0
      elif req['type'] == list:
        req['fallback'] = []
      elif req['type'] == dict:
        req['fallback'] = []

    if req['name'] not in data:
      data[req['name']] = req['fallback'].replace(' ', '').split(',') if 'list' in req and req['list'] else req['fallback']
    else:
      # format data - CHECK
      # list string YO! - CHECK
      # check if data available and right - CHECK
      key = req['name']
      if isinstance(data[key], list) and req['type'] != list and len(data[key]) == 1:
        data[key] = data[key][0]

      if isinstance(data[key], str):
        data[key] = data[key].lower()

      if isinstance(data[key], str):
        if req['type'] == bool:
          if data[key] == 'true':
            data[key] = True
          elif data[key] == 'false':
            data[key] = False
          else:
            data[key] = req['fallback']

        elif req['type'] == int:
          data[key] = int(data[key]) if data[key].isdigit() else req['fallback']

        elif req['type'] == float:
          try:
            data[key] = float(data[key])
          except:
            data[key] = req['fallback']
      elif isinstance(data[key], int) or isinstance(data[key], float):
        if req['type'] == bool:
          if int(data[key]) == 1:
            data[key] = True
          elif int(data[key]) == 0:
            data[key] = False
          else:
            data[key] = req['fallback']

      if not isinstance(data[key], req['type']):
        data[key] = req['fallback']

      if isinstance(data[key], str):
        if 'list' in req and req['list']:
          data[key] = data[key].replace(' ', '').split(',')

      if 'restricted' in req:
        flatrestrictive = [(x if isinstance(x, str) else x['name']) for x in req['restricted']]
        dictrestrictive = {}
        [dictrestrictive.update({x['name']: x['fallback']}) for x in req['restricted'] if isinstance(x, dict)]

      if req['type'] == str and isinstance(data[key], list) and 'restricted' in req:
        for pointer in range(len(data[key])):
          if data[key][pointer] in flatrestrictive:
            if data[key][pointer] in dictrestrictive.keys():
              data[key][pointer] = dictrestrictive[data[key][pointer]]
          else:
            data[key][pointer] = req['fallback']
            if hardmode:
              code = 400
      elif 'restricted' in req:
        if data[key] in flatrestrictive:
          if data[key] in dictrestrictive.keys():
            data[key] = dictrestrictive[data[key]].replace(' ', '').split(',') if 'list' in req and req['list'] else dictrestrictive[data[key]]
        else:
          data[key] = req['fallback']
          if hardmode:
            code = 400

  if restrictive:
    required = [y['name'] for y in required]
    output = {}

    for key, value in data.items():
      if key in required:
        output[key] = value
    print(output)
    return output, code
  else:
    return data, code
