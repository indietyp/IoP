# import os
# import flaskr
import unittest
from IoP import app
import urllib.parse
import tools.logger
import json
import random
import logging
import datetime
logger = logging.getLogger('exception')


class RESTfulTestReadOnly(unittest.TestCase):
  def setUp(self):
    app.config['TESTING'] = True
    self.app = app.test_client()

  def tearDown(self):
    pass

  def test_plants_get(self):
    for setting in ['minimal', 'normal', 'detailed', 'extensive', 'master', 'satisfaction', 'sensorsatisfaction', 'satisfaction,master,extensive', 'satisfaction,', 'default']:
      for mode in [True, False]:
        query = urllib.parse.urlencode({'select': setting, 'dict': str(mode).lower()})
        check = self.app.get('/plants?{}'.format(query), follow_redirects=True)
        if setting == 'extensive' and mode:
          comparison = check.data
        logger.info(check.data)

    selected = random.choice(json.loads(comparison.decode())['content'])
    for setting in ['intervals', 'created_at', 'type', 'species', 'survived', 'location', 'full', 'default']:
      query = urllib.parse.urlencode({'select': setting})
      check = self.app.get('/plants/{}?{}'.format(selected['uuid'], query), follow_redirects=True)

    for setting in ['range', 'default']:
      query = urllib.parse.urlencode({'select': setting})
      check = self.app.get('/plants/{}/sensor?{}'.format(selected['uuid'], query), follow_redirects=True)

    for setting in ['latest', 'prediction', 'data', 'current', 'range', 'extreme', 'count', 'timespan', 'default']:
      data = {'select': setting, 'max': 'true', 'ever': 'true', 'backlog': 'true'}

      if setting == 'timespan':
        data['start'] = str(datetime.datetime.now().timestamp() - 600)
        data['stop'] = str(datetime.datetime.now().timestamp())
      else:
        data['start'] = 0
        data['stop'] = 10

      query = urllib.parse.urlencode(data)
      check = self.app.get('/plants/{}/sensor/temperature?{}'.format(selected['uuid'], query), follow_redirects=True)

    for setting in ['email', 'wizard', 'name', 'full', 'default']:
      query = urllib.parse.urlencode({'select': setting})
      check = self.app.get('/plants/{}/responsible?{}'.format(selected['uuid'], query), follow_redirects=True)

    for setting in ['average', 'online']:
      query = urllib.parse.urlencode({'select': setting})
      check = self.app.get('/plants/{}/responsible?{}'.format(selected['uuid'], query), follow_redirects=True)

    print('\nfinished plants')

  # done
  def test_persons_get(self):
    for setting in ['minimal', 'normal', 'detailed', 'extensive', 'default']:
      for mode in [False, True]:
        query = urllib.parse.urlencode({'select': setting, 'dict': str(mode).lower()})
        check = self.app.get('/persons?{}'.format(query), follow_redirects=True)
        logger.info(check.data)
        if setting == 'extensive' and mode:
          comparison = check.data

    selected = random.choice(json.loads(comparison.decode())['content'])
    for setting in ['full', 'default']:
      query = urllib.parse.urlencode({'select': setting})
      check = self.app.get('/persons/{}?{}'.format(selected['uuid'], query), follow_redirects=True)
      self.assertEqual(json.loads(check.data.decode())['content'], selected)

    print('\nfinished persons')

  # done
  def test_sensors_get(self):
    for setting in ['minimal', 'normal', 'detailed', 'extensive', 'default']:
      for mode in [True, False]:
        query = urllib.parse.urlencode({'select': setting, 'dict': str(mode).lower()})
        check = self.app.get('/sensors?{}'.format(query), follow_redirects=True)
        logger.info(check.data)

        if setting == 'extensive' and mode:
          comparison = check.data

    selected = random.choice(json.loads(comparison.decode())['content'])
    for setting in ['range', 'unit', 'full', 'default']:
      query = urllib.parse.urlencode({'select': setting})
      check = self.app.get('/sensors/{}?{}'.format(selected['uuid'], query), follow_redirects=True)

      compared = json.loads(check.data.decode())['content']
      if setting in ['full', 'default']:
        self.assertEqual(compared, selected)
      elif setting in ['unit']:
        self.assertEqual(compared, {setting: selected[setting]})
      elif setting in ['range']:
        self.assertEqual(compared, {'min_value': selected['min_value'], 'max_value': selected['max_value']})

    print('\nfinished sensors')

  # done
  def test_misc_get(self):
    for setting in ['minimal', 'normal', 'detailed', 'extensive', 'default']:
      for mode in [True, False]:
        for registered in [True, False]:
          query = urllib.parse.urlencode({'select': setting, 'dict': str(mode).lower(), 'registered': str(registered).lower()})
          check = self.app.get('/discover?{}'.format(query), follow_redirects=True)
          logger.info(check.data)

    check = self.app.get('/day/night', follow_redirects=True)
    check = self.app.get('/host', follow_redirects=True)

    print('\nfinished discover')

if __name__ == '__main__':
  unittest.main()
