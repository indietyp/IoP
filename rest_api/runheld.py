from IoP import app
from meinheld import server

DEBUG = True

if __name__ == '__main__':
  server.listen(("0.0.0.0", 2902))
  server.run(app)
