from peewee import *
from settings.database import DATABASE_NAME
from models.plant import Plant
import uuid

db = SqliteDatabase(DATABASE_NAME)


class DayNightTime(Model):
  uuid = UUIDField(default=uuid.uuid4)
  plant = ForeignKeyField(Plant, null=True)

  start = IntegerField(default=900)  # 900
  stop = IntegerField(default=2400)  # 2400

  display = BooleanField(default=False)
  ledbar = BooleanField(default=False)
  generalleds = BooleanField(default=False)
  notification = BooleanField(default=False)

  class Meta:
    database = db
