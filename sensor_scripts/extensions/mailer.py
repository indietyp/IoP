# from marrow.mailer import Message, Mailer
# from pymongo import MongoClient
# import pymongo
# from ..tools.main import Tools
# from ..tools.security import KeyChain
from models.sensor import SensorStatus, SensorCount, SensorSetting


class PlantMailer(object):
  def __init__(self):
    pass

  def send(self, data):
    """ data
          sensor - sensor object
          value - current value
          satisfaction - current satisfaction
    """
    if data['satisfaction'] == 'danger':
      pass
    pass


if __name__ == "__main__":
  pass
