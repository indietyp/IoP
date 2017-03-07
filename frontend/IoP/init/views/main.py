from IoP import app
from flask import redirect, url_for, render_template, session


def index():
  return 'placeholder'


@app.route('/introduction')
def introduction():
  # if 'step' not in session:
  #   session['step'] = 1
  session['step'] = 1

  if session['step'] >= 1:
    session['step'] = 2
    return render_template('init/introduction.jade', content={'get': True, 'discover': True})
  return 'failed request, I\'m so sorry!'


@app.route('/information')
def information():
  if session['step'] >= 2:
    session['step'] = 3
    return render_template('init/information.jade', content={'get': True})
  return 'failed request, I\'m so sorry!'


@app.errorhandler(404)
def page_not_found(*args, **kwagrs):
  return redirect(url_for('introduction'))
