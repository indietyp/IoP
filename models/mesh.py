from peewee import *
import uuid
from settings.database import DATABASE_NAME

from models.plant import Plant

db = SqliteDatabase(DATABASE_NAME)


class MeshMessage(Model):
  plant = ForeignKeyField(Plant)
  sender = ForeignKeyField(Plant, null=True)
  received = BooleanField(default=True)

  uuid = UUIDField(unique=True, default=uuid.uuid4)
  priority = SmallIntegerField()

  code = IntegerField(null=True)
  a_message = CharField(null=True)
  b_message = CharField(null=True)
  c_message = CharField(null=True)
  d_message = CharField(null=True)

  class Meta:
    database = db
