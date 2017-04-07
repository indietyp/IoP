import sys

PLANTS_GET = [{'name': 'select',
               'type': str,
               'restricted': ['master',
                              'normal',
                              'minimal',
                              'detailed',
                              'extensive',
                              'satisfaction',
                              'sensorsatisfaction',
                              {'name': 'default', 'fallback': 'normal'}],
               'list': True,
               'fallback': 'normal'},
              {'name': 'dict', 'type': bool, 'fallback': True}]

PLANTS_PUT = [{'name': 'register', 'type': bool, 'fallback': False},
              {'name': 'name', 'type': str},
              {'name': 'location', 'type': str},
              {'name': 'species', 'type': int},
              {'name': 'ip', 'type': str},
              {'name': 'uuid', 'type': str},
              {'name': 'email', 'type': str},
              {'name': 'persistant_hold', 'type': str},
              {'name': 'role', 'type': str}]

PLANT_GET = [{'name': 'select',
              'type': str,
              'restricted': ['created_at',
                             'intervals',
                             'survived',
                             'location',
                             'species',
                             'full',
                             {'name': 'type', 'fallback': 'species'},
                             {'name': 'default', 'fallback': 'full'}],
              'list': True,
              'fallback': 'full'}]

PLANT_POST = [{'name': 'mode', 'type': str, 'restricted': ['online', 'offline', 'reset', 'add']},
              {'name': 'name', 'type': str},
              {'name': 'species', 'type': int},
              {'name': 'location', 'type': str},
              {'name': 'ranges', 'type': bool, 'fallback': False},
              {'name': 'range', 'type': int, 'fallback': 0},
              {'name': 'responsible', 'type': bool},
              {'name': 'email', 'type': str},
              {'name': 'firstname', 'type': str},
              {'name': 'satisfaction', 'type': bool, 'fallback': False},
              {'name': 'alive', 'type': bool, 'fallback': False},
              {'name': 'notification', 'type': bool, 'fallback': False},
              {'name': 'connection-lost', 'type': bool, 'fallback': False},
              {'name': 'non-persistant', 'type': bool, 'fallback': False},
              {'name': 'seconds', 'type': int},
              {'name': 'minutes', 'type': int},
              {'name': 'hours', 'type': int},
              {'name': 'days', 'type': int}]

PLANT_SENSORS_GET = [{'name': 'select',
                      'type': str,
                      'restricted': ['range',
                                     {'name': 'default', 'fallback': 'range'}],
                      'list': True,
                      'fallback': 'range'}]

PLANT_SENSOR_GET = [{'name': 'select',
                     'type': str,
                     'restricted': ['latest',
                                    'prediction',
                                    'data',
                                    'current',
                                    'range',
                                    'extreme',
                                    'count',
                                    'timespan',
                                    {'name': 'default', 'fallback': 'data'}],
                     'list': True,
                     'fallback': 'data'},
                    {'name': 'max', 'type': bool},
                    {'name': 'ever', 'type': bool},
                    {'name': 'backlog', 'type': bool},
                    {'name': 'start', 'type': int},
                    {'name': 'stop', 'type': int, 'fallback': sys.maxsize}]

PLANT_RESPONSIBLE_GET = [{'name': 'select',
                          'type': str,
                          'restricted': ['email',
                                         'wizard',
                                         'full',
                                         {'name': 'default', 'fallback': 'full'}],
                          'list': True,
                          'fallback': 'full'}]

PLANT_STATUS_GET = [{'name': 'select',
                     'type': str,
                     'restricted': ['average',
                                    'online',
                                    {'name': 'default', 'fallback': 'average'}],
                     'list': True,
                     'fallback': 'average'}]

PLANT_MESSAGE_GET = [{'name': 'select',
                      'type': str,
                      'restricted': ['full',
                                     {'name': 'default', 'fallback': 'full'}],
                      'list': True,
                      'fallback': 'full'}]

SENSORS_GET = [{'name': 'select',
                'type': str,
                'restricted': ['minimal',
                               'normal',
                               'detailed',
                               'extensive',
                               {'name': 'default', 'fallback': 'normal'}],
                'list': True,
                'fallback': 'normal'},
               {'name': 'dict', 'type': bool, 'fallback': True}]

SENSOR_GET = [{'name': 'select',
               'type': str,
               'restricted': ['range',
                              'unit',
                              'full',
                              {'name': 'default', 'fallback': 'full'}],
               'list': True,
               'fallback': 'full'}]

PERSONS_GET = [{'name': 'select',
                'type': str,
                'restricted': ['minimal',
                               'normal',
                               'detailed',
                               'extensive',
                               {'name': 'default', 'fallback': 'normal'}],
                'list': True,
                'fallback': 'normal'},
               {'name': 'dict', 'type': bool, 'fallback': True}]

PERSONS_PUT = [{'name': 'name', 'type': str},
               {'name': 'email', 'type': str},
               {'name': 'wizard', 'type': bool}]

PERSON_GET = [{'name': 'select',
               'type': str,
               'restricted': ['full',
                              {'name': 'default', 'fallback': 'ful'}],
               'list': True,
               'fallback': 'full'}]

PERSON_POST = [{'name': 'name', 'type': str},
               {'name': 'email', 'type': str},
               {'name': 'wizard', 'type': bool}]

MESSAGES_GET = [{'name': 'select',
                 'type': str,
                 'restricted': ['minimal',
                                'normal',
                                'detailed',
                                'extensive',
                                {'name': 'default', 'fallback': 'normal'}],
                 'list': True,
                 'fallback': 'normal'},
                {'name': 'dict', 'type': bool, 'fallback': True}]

MESSAGES_PUT = [{'name': 'heading', 'type': str},
                {'name': 'message', 'type': str}]

MESSAGE_GET = [{'name': 'select',
                'type': str,
                'restricted': ['nessage',
                               'full',
                               {'name': 'default', 'fallback': 'full'}],
                'list': True,
                'fallback': 'full'},
               {'name': 'dict', 'type': bool, 'fallback': True}]

MESSAGE_POST = [{'name': 'heading', 'type': str},
                {'name': 'message', 'type': str},
                {'name': 'person', 'type': bool},
                {'name': 'plant', 'type': str}]

DISCOVER_GET = [{'name': 'select',
                 'type': str,
                 'restricted': ['minimal',
                                'normal',
                                'detailed',
                                'extensive',
                                {'name': 'default', 'fallback': 'normal'}],
                 'list': True,
                 'fallback': 'normal'},
                {'name': 'dict', 'type': bool, 'fallback': True},
                {'name': 'registered', 'type': bool, 'fallback': False}]

DISCOVER_POST = [{'name': 'execute', 'type': bool}]

DAYNIGHT_GET = [{'name': 'select',
                 'type': str,
                 'restricted': ['full',
                                {'name': 'default', 'fallback': 'full'}],
                 'list': True,
                 'fallback': 'full'}]

DAYNIGHT_POST = [{'name': 'stop', 'type': int},
                 {'name': 'start', 'type': int},
                 {'name': 'ledbar', 'type': bool},
                 {'name': 'display', 'type': bool},
                 {'name': 'generalleds', 'type': bool},
                 {'name': 'notitification', 'type': bool}]

HOST_GET = [{'name': 'select',
             'type': str,
             'restricted': ['full',
                            {'name': 'default', 'fallback': 'full'}],
             'list': True,
             'fallback': 'full'}]
