from flask import Flask, request

app = Flask(__name__)


# @app.before_request
# def time_start():
#   session['now'] = datetime.datetime.now()


@app.after_request
def time_stop(response_class):
  print(response_class.data.decode())
  return response_class


import IoP.views.get
import IoP.views.update
import IoP.views.insert
import IoP.views.execute
import IoP.views.delete

import IoP.main
import IoP.misc
import IoP.plant
import IoP.sensor
import IoP.person
import IoP.message
