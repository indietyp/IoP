from peewee import *
from models.main import Base
# from settings.database import DATABASE_NAME
# db = SqliteDatabase(DATABASE_NAME)


class KeyChain(Base):
  secret      = TextField()
  message     = TextField()

  application = CharField()


class MailAccount(Base):
  account     = CharField()
  transport   = CharField(default='smtp')
  server      = CharField()
  encryption  = CharField(default='ssl')
  port        = IntegerField(default=465)

  daemon      = BooleanField(default=False)
  password    = ForeignKeyField(KeyChain)
