from flask import Flask, session, render_template
# from slimish_jinja import SlimishExtension


app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.secret_key = 'uyfo2346tr3r3urey8f138r9pfr1vy3ofydv'

import IoP.views.general
import IoP.views.plants
import IoP.views.get.plants
