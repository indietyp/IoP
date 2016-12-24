from IoP import app
from meinheld import server

DEBUG = True
server.listen(("0.0.0.0", 5000))
server.run(app)
