from pymongo import MongoClient
from cryptography.fernet import Fernet

class KeyChain:
  def __init__(self):
    client = MongoClient()
    self.db = client.pot

  def create(self, application, name):
    message = encrypt(name)
    self.db.KeyChain.insert_one({'application': application, 'message': message})

  def read(self, application):
    message = self.db.KeyChain.find_one({'application': application})
    return self.decrypt(message)

  def decrypt(self, message):
    algo = Fernet(message[0])
    decrypted = algo.decrypt(bytes(message[1], encoding= 'ascii'))

    return [decrypted]

  def encrypt(self, message):
    key = Fernet.generate_key()

    algo = Fernet(key)
    encrypted = algo.encrypt(bytes(name, encoding= 'ascii'))

    return [key, encrypted]
