from IoP import app, init
from flask import render_template, redirect, url_for, request
from IoP import init, init_overview
import random
import json


@app.route('/')
def index():
  content = init()
  content.update({'error': request.args.get('error', '')})
  content.update({'current_active': 'overview'})
  return render_template('general/redirect.jade', content=content)


@app.errorhandler(404)
def page_not_found(e):
  message = 'not valid url'
  if random.random() > 0.9:
    if random.random() > 0.5:
      message = 'PRAISE THE ALL MIGHTY UNICORN (' + message + ')'
    else:
      message = 'BEEP BOOP ROBOT VOICES (' + message + ')'

  return redirect(url_for('index', error=message))


@app.route('/add')
def add_plant():
  content = init()
  content.update({'get': True, 'current_active': 'add plant'})
  return render_template('general/add.jade', content=content)


@app.route('/manage')
def manage_plants():
  content = init()
  content.update({'get': True, 'current_active': 'manage plants'})
  return render_template('general/manage.jade', content=content)


@app.route('/global/settings')
def global_settings():
  content = init()
  content.update({'current_active': 'Global Settings', 'type': 'setting'})
  return render_template('general/settings.jade', content=content)
