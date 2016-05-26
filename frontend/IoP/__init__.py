from flask import Flask
# from slimish_jinja import SlimishExtension


app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

import IoP.views.general
