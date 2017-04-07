import json
from IoP import app
from IoP.config import *
from flask import make_response


class TypeEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj.__class__, type):
      return obj.__name__

    # Let the base class default method raise the TypeError
    return json.JSONEncoder.default(self, obj)


@app.route('/', methods=['GET'])
def describing():
  output = {'/plants': {'get': PLANTS_GET,
                        'put': PLANTS_PUT},
            "/plants/<p_uuid>": {'get': PLANT_GET,
                                 'post': PLANT_POST},
            '/plants/<p_uuid>/sensor': {'get': PLANT_SENSORS_GET},
            '/plants/<p_uuid>/sensor/<s_uuid>': {'get': PLANT_SENSOR_GET},
            '/plants/<p_uuid>/responsible': {'get': PLANT_RESPONSIBLE_GET},
            '/plants/<p_uuid>/status': {'get': PLANT_STATUS_GET},
            '/plants/<p_uuid>/message': {'get': PLANT_MESSAGE_GET},
            '/sensors': {'get': SENSORS_GET},
            '/sensors/<s_uuid>': {'get': SENSOR_GET},
            '/persons': {'get': PERSONS_GET,
                         'put': PERSONS_PUT},
            '/persons/<r_uuid>': {'get': PERSON_GET,
                                  'post': PERSON_POST,
                                  'delete': []},
            '/messages': {'get': MESSAGES_GET,
                          'put': MESSAGES_PUT},
            '/messages/<m_uuid>': {'get': MESSAGE_GET,
                                   'post': MESSAGE_POST},
            '/discover': {'get': DISCOVER_GET,
                          'post': DISCOVER_POST},
            '/day/night': {'get': DAYNIGHT_GET,
                           'post': DAYNIGHT_POST},
            '/host': {'get': HOST_GET,
                      'post': {}}}

  converted = json.dumps({'code': 200, 'content': output}, cls=TypeEncoder)
  response = make_response(converted)
  response.mimetype = 'application/json'
  return response
  # return data_formatting(data=output)
