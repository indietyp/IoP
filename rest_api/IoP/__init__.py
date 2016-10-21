from flask import Flask, session, render_template

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.secret_key = 'n2u2ienei3rJDSAUo2jaid3KFOsnwof123'


import IoP.views.get
import IoP.views.update
import IoP.views.insert
import IoP.views.execute
