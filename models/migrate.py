import sys
from peewee_migrate import Router
from settings.database import DATABASE_NAME
from peewee import SqliteDatabase
import inspect
from inspect import isfunction
from peewee import BaseModel

router = Router(SqliteDatabase(DATABASE_NAME))

# try:
if sys.argv[1] == 'makemigrations':
  models = []
  for module in ['plant', 'sensor', 'people', 'security', 'mesh']:
    exec('import ' + module)
    models.extend([
      obj for name, obj in inspect.getmembers(
          eval(module), lambda obj: not isfunction(obj) and isinstance(obj, BaseModel) and obj.__name__ != 'Model'
      )
    ])

  print(models)
  # Create migration
  router.create('models', auto=models)

elif sys.argv[1] == 'migrate':
  router.run()
else:
  print('sry, but this is not a valid command \n\n')
  print('try: makemigrations or migrate')

# except:
#   print('not specified anything')
