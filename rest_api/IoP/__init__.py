from flask import Flask, session, render_template
import datetime

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.secret_key = 'n2u2ienei3rJDSAUo2jaid3KFOsnwof123'


@app.before_request
def time_start():
  session['now'] = datetime.datetime.now()


@app.after_request
def time_stop(response_class):
  print(datetime.datetime.now() - session['now'])
  return response_class


import IoP.views.get
# import IoP.views.update
# import IoP.views.insert
# import IoP.views.execute
# import IoP.views.delete
