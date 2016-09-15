from IoP import app
from flask import request
from models.plant import Person
import json


@app.route('/create/responsible', methods=['POST'])
def create_plant_name():
  person = Person()
  person.name = request.form['name']
  person.email = request.form['email']
  person.wizard = True if request.form['wizard'] == 'True' else False
  person.save()

  return json.dumps({'info': 1})

@app.route('/create/plant', methods=['POST'])
def create_plant():
  pass
