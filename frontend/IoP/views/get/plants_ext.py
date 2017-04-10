import json
from IoP import app
import urllib.parse
import urllib.request
from flask import session, request


@app.route('/get/notification/message/names', methods=['POST'])
def get_message_name():
  query = urllib.parse.urlencode({'select': 'extensive'})
  with urllib.request.urlopen('http://localhost:2902/messages?{}'.format(query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(data)


@app.route('/get/notification/message/content', methods=['POST'])
def get_message_content():
  message_uuid = request.form['uuid']
  if message_uuid == '':
    return ''

  query = urllib.parse.urlencode({'select': 'message'})
  with urllib.request.urlopen('http://localhost:2902/messages/{}?{}'.format(message_uuid, query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(data)


@app.route('/submit/notification/message', methods=['POST'])
def insert_message():
  data = urllib.parse.urlencode({
      'heading': request.form['name'],
      'text': request.form['message'],
      'plant': session['p_uuid'],
      'person': request.form['responsible']}).encode('ascii')

  if 'uuid' in request.form.keys():
    req = urllib.request.Request('http://localhost:2902/messages/{}'.format(request.form['uuid']), data, 'POST')
  else:
    req = urllib.request.Request('http://localhost:2902/messages'.format(request.form['uuid']), data, 'PUT')
  urllib.request.urlopen(req)

  return {'code': 'ok'}


@app.route('/remove/responsible', methods=['POST'])
def delete_responsible():
  data = urllib.parse.urlencode({})
  req = urllib.request.Request('http://localhost:2902/persons/{}'.format(request.form['uuid']), data, 'DELETE')
  urllib.request.urlopen(req)

  return {'code': 'ok'}


@app.route('/change/responsible', methods=['POST'])
def update_responsible():
  data = urllib.parse.urlencode({
      'name': request.form['name'],
      'email': request.form['email']}).encode('ascii')

  req = urllib.request.Request('http://localhost:2902/persons/{}'.format(request.form['uuid']), data, 'POST')
  urllib.request.urlopen(req)

  return {'code': 'ok'}


@app.route('/change/responsible/wizard', methods=['POST'])
def change_responsible_wizard():
  data = urllib.parse.urlencode({'wizard': True}).encode('ascii')

  req = urllib.request.Request('http://localhost:2902/persons/{}'.format(request.form['uuid']), data, 'POST')
  urllib.request.urlopen(req)

  return {'code': 'ok'}


@app.route('/change/plant/intervals', methods=['POST'])
def change_plant_intervals():
  data = urllib.parse.urlencode({'minutes': request.form['connection'], 'connection-lost': True}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/plants/{}'.format(session['p_uuid']), data)
  urllib.request.urlopen(req)

  data = urllib.parse.urlencode({'hours': request.form['notification'], 'notification': True}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/plants/{}'.format(session['p_uuid']), data)
  urllib.request.urlopen(req)

  data = urllib.parse.urlencode({'days': request.form['non_persistant'], 'non-persistant': True}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/plants/{}'.format(session['p_uuid']), data)
  urllib.request.urlopen(req)

  return json.dumps({'info': 'success'})


@app.route('/create/responsible/none', methods=['POST'])
def createResponsible():
  wizard = True if request.form['wizard'] == 'yes' else False
  data = urllib.parse.urlencode({'email': request.form['email'], 'name': request.form['name'], 'wizard': wizard}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/persons', data, 'PUT')
  urllib.request.urlopen(req)

  return json.dumps({'info': 'success'})


@app.route('/get/plant/notification/message', methods=['POST'])
def get_plant_notification_message():
  query = urllib.parse.urlencode({'select': 'full'})
  with urllib.request.urlopen('http://localhost:2902/plants/{}/message?{}'.format(session['p_uuid'], query)) as response:
    data = json.loads(response.read().decode('utf8'))['content']

  return json.dumps(data)
