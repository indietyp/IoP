from flask import Flask, session, render_template
from pymongo import MongoClient

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.secret_key = 'n2u2ienei3rJDSAUo2jaid3KFOsnwof123'
# client = Connection()
# db = client['iop']

import IoP.views.get
import IoP.views.update

# if __name__ == '__main__':

