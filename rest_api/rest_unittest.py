import json
import IoP
import unittest
import datetime
from pymongo import MongoClient

class IoP_rest_api_unittest(unittest.TestCase):

  def setUp(self):
    client = MongoClient()
    self.db = client.iop
    IoP.app.config['TESTING'] = True
    self.app = IoP.app.test_client()

  def tearDown(self):
      pass

  def test_plant_location(self):
    document = self.db.Plant.find_one()
    name = document['name']
    location = document['location']
    assert bytes(location, encoding="UTF-8") in self.app.get('/get/plant/' + name + '/location').data

  def test_plant_survived(self):
    document = self.db.Plant.find_one()
    name = document['name']
    difference = datetime.datetime.now() - document['created_at']
    assert bytes(json.dumps(float(difference.days)), encoding='UTF-8') in self.app.get('/get/plant/' + name + '/created_at').data
if __name__ == '__main__':
    unittest.main()
