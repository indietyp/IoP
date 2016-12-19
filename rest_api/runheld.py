from IoP import app
from meinheld import server

DEBUG = True
server.listen(("0.0.0.0", 2902))
server.run(app)
