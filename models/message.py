from peewee import *
import datetime
from models.plant import Person
from settings.database import DATABASE_NAME
from models.plant import *
import uuid

db = SqliteDatabase(DATABASE_NAME)


class MessagePreset(Model):
  name = CharField(unique=True)
  uuid = UUIDField(default=uuid.uuid4)

  creator = ForeignKeyField(Person, null=True)
  message = TextField()
  created_at = DateTimeField(default=datetime.datetime.now)
  default = BooleanField(default=False)

  class Meta:
    database = db
