from IoP import app
from flask import redirect, url_for, render_template, session


@app.route('/')
def index():
  if 'step' not in session or session['step'] == 0:
    session['step'] = 0
    return render_template('init/introduction.jade', content={'get': True})
  return 'failed request, I\'m so sorry!'


@app.errorhandler(404)
def page_not_found(*args, **kwagrs):
  return redirect(url_for('index'))
