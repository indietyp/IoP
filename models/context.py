import uuid
from peewee import *
from models.main import Base
from models.plant import Plant
# from settings.database import DATABASE_NAME
# db = SqliteDatabase(DATABASE_NAME)


class DayNightTime(Base):
  uuid = UUIDField(default=uuid.uuid4)
  plant = ForeignKeyField(Plant, null=True)

  start = IntegerField(default=900)  # 900
  stop = IntegerField(default=2400)  # 2400

  display = BooleanField(default=False)
  ledbar = BooleanField(default=False)
  generalleds = BooleanField(default=False)
  notification = BooleanField(default=False)
