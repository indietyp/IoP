from IoP import app
import meinheld

DEBUG = True
meinheld.listen(("0.0.0.0", 2902))
meinheld.run(app)
