# from pymongo import MongoClient
from cryptography.fernet import Fernet
from models.security import MailAccount


class KeyChain(object):
  def __init__(self):
    pass

  def decrypt(self, secret, message):
    algo = Fernet(secret)
    decrypted = algo.decrypt(bytes(message, encoding='utf-8'))

    return decrypted.decode()

  def encrypt(self, message):
    key = Fernet.generate_key()

    algo = Fernet(key)
    encrypted = algo.encrypt(bytes(message, encoding='utf-8'))

    return [key, encrypted]

# KeyChain().create('mailer', 'x97y3bY89@')

if __name__ == "__main__":
  notification_account = MailAccount.select()\
                                    .where(MailAccount.daemon == True)[0]

  crypt_pwd = notification_account.password
  password = KeyChain().decrypt(crypt_pwd.secret, crypt_pwd.message)
  print(password)
