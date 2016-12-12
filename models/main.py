from peewee import *
from settings.database import DATABASE_NAME
from peewee import BaseModel
import inspect
from inspect import isfunction
from plant import *
from sensor import *
from people import *
from security import *


if __name__ == '__main__':
  db = SqliteDatabase(DATABASE_NAME)
  models = []

  for module in ['plant', 'sensor', 'security', 'context']:
    exec('import ' + module)
    models.extend([
      obj for name, obj in inspect.getmembers(
          eval(module), lambda obj: not isfunction(obj) and isinstance(obj, BaseModel) and obj.__name__ != 'Model'
      )
    ])

  print(models)
  db.create_tables(models)
