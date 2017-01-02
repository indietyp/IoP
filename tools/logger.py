import sys
import logging
import traceback
import logging.config
from settings.logging import LOCATIONS, LOGLEVEL

LOGGING = {
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '[%(asctime)s] [%(process)d] [%(levelname)-8s] [%(module)s] [%(funcName)-8s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'filters': {},
    'handlers': {},
    'loggers': {}
}

for name, location in LOCATIONS.items():
  LOGGING['handlers'][name + '_handler'] = {
      'class': 'logging.FileHandler',
      'formatter': 'detailed',
      'filename': location
  }

  LOGGING['loggers'][name] = {
      'level': LOGLEVEL,
      'handlers': [name + '_handler']
  }
logging.config.dictConfig(LOGGING)


def exception_handler(type, value, tb):
  logger = logging.getLogger('exception')
  message = "Uncaught exception: {0}: {1} \n".format(str(value.__class__.__name__), str(value))
  for trace in traceback.format_tb(tb):
    message += trace
  logger.error(message)


sys.excepthook = exception_handler
