from pymongo import MongoClient

# NEW COLLECTION = Pictures, ApplicationData
# ApplicationData -> 90% per plant (als could be Plant! idk right now)
# PLANT NEW FIELD! CONFIG!

client = MongoClient()
db = client.iop

# collection = db.SensorType.find()

# i = 0
# for document in collection:
#   result = db.SensorType.update_one(
#     document, {'$set':{'s_id': i}})
#   i += 1
#   print(result.modified_count)
#   print(result.matched_count)


# collection = db.Plant.find()

# i = 0
# for document in collection:
#   if 'picture' in document:
#     data = document['picture']
#   else:
#     data = ''
#   # print(document)
#   result = db.Plant.update_one(
#     {'_id': document['_id']},
#     {
#       '$unset': {
#         'response_id': ''
#       },
#       '$set': {
#         'responsible_id': 0
#       }
#     }
#     )
#   i += 1
#   print(result.modified_count)
#   print(result.matched_count)

# collection = db.Plant.find()
# for document in collection:
#   print(document['name'][0:1])
#   coolGuy = {'sensor_settings': []}
#   for subdocument in db.SensorType.find():
#     migrated_collection = db.PlantConfig.find_one({'a': document['name'][0:1], 's': subdocument['t'][0:1]})
#     # coolGuy = {'sensor_settings': {'green': {}, 'yellow': {}}}
#     coolGuy['sensor_settings'].append({'sensor_id': subdocument['s_id'], 'settings': {'green': migrated_collection['o'], 'yellow': migrated_collection['w']}})
#     print('- ' + subdocument['t'][0:1])
#     print(coolGuy)
#   result = db.Plant.update_one(
#   {'_id': document['_id']},
#   {
#     # '$unset': {
#     #   'response_id': ''
#     # },
#     '$set': coolGuy
#   }
#   )
#   print(result.modified_count)
#   print(result.matched_count)

# i = 0
# collection.SensorData.find()
# for document in collection:
#   if document['a'] == 'm':
#     i = 1
#   else:
#     i = 0
#    result = db.Plant.update_one(
#   {'_id': document['_id']},
#   {
#     '$unset': {
#       'a': ''
#     },
#     '$set': { 'sid': i}
#   }
#   )

# result = db.SensorData.update_many(
#   {'s': 'm'},
#   {
#     # '$unset': {
#     #   'sid': ''
#     # },
#     '$set': { 's': 3}
#   }
#   )

# print(result.modified_count)
# print(result.matched_count)

# i = 0
# for document in db.ResponsiblePerson.find():
#   try:
#     new = document['person']
#     result = db.ResponsiblePerson.update_one(
#       {'_id': document['_id']},
#       {
#       '$unset': {
#         'person': ''
#       },
#       '$set': {
#         'username': new
#       }
#       }
#       )
#     print(result.modified_count)
#     print(result.matched_count)
#   except:
#     pass
# result = db.ResponsiblePerson.update_one(
#     {'email': 'Bilal-23@gmx.de'},
#     {
#     '$set': {
#       'wizard': True
#     }
#     }
#     )

# result = db.Plant.update_one(
#   {'name': 'paul'},
#   {'$set':{'responsible_id': 1}}
#   )

# print(result.modified_count)

# LIGHT = RED
# EXISTS RED?
#   NO
#   EXISTS YELLOW?
#     YES
# INSERT LIGHT
#   REMOVE OLD, INSERT NEW
# CHECKUP -> CHANGE
#   YELLOW NOW RED ->
#     reset counter to 0
#     counter++
# LIGHT RED COUNTER++

result = db.Plant.update_one(
  {'name': 'paul'},
  {
    '$unset': {
      'alive': 0
    },
    '$set': {
      'offline': [0, 12],
      'online': [6, 24],
      'sensor_status': [{
        "yellow" : ["light", "humidity", "temperature"],
        "red" : [],
        "green" : ["moisture"]
      }, {
        'current_counter': 12,
        'overall_counter': {
          'light': {
            'green': 0,
            'yellow': 2,
            'red': 7
          },
          'temperature': {
            'green': 0,
            'yellow': 2,
            'red': 7
          },
          'humidity': {
            'green': 0,
            'yellow': 2,
            'red': 7
          },
          'moisture': {
            'green': 0,
            'yellow': 2,
            'red': 7
          }
        }
      }]
    }
  }
  )
# ranges = db.Plant.find_one()['sensor_settings']
# s_id = ''
# for rang in ranges:
#   s_id = rang['settings'] if rang['sensor_id'] == 0 else s_id
# # print(s_id)

# yellow_counter = 0
# green_counter = 0
# red_counter = 0
# for document in db.SensorData.find({'p': 0, 's':0}):
#   if document['v'] >= s_id['yellow']['min'] and document['v'] <= s_id['yellow']['max']:
#     if document['v'] >= s_id['green']['min'] and document['v'] <= s_id['green']['max']:
#       green_counter+=1
#     else:
#       yellow_counter+=1
#   else:
#     red_counter+=1
#   pass

# print('TEMPERATURE')
# print('RED: ' + str(red_counter))
# print('YELLOW: ' + str(yellow_counter))
# print('GREEN: ' + str(green_counter))

# s_id = ''
# for rang in ranges:
#   s_id = rang['settings'] if rang['sensor_id'] == 1 else s_id
# # print(s_id)

# yellow_counter = 0
# green_counter = 0
# red_counter = 0
# for document in db.SensorData.find({'p': 0, 's':1}):
#   if document['v'] >= s_id['yellow']['min'] and document['v'] <= s_id['yellow']['max']:
#     if document['v'] >= s_id['green']['min'] and document['v'] <= s_id['green']['max']:
#       green_counter+=1
#     else:
#       yellow_counter+=1
#   else:
#     red_counter+=1
#   pass

# print('HUMIDITY')
# print('RED: ' + str(red_counter))
# print('YELLOW: ' + str(yellow_counter))
# print('GREEN: ' + str(green_counter))

# s_id = ''
# for rang in ranges:
#   s_id = rang['settings'] if rang['sensor_id'] == 2 else s_id
# # print(s_id)

# yellow_counter = 0
# green_counter = 0
# red_counter = 0
# for document in db.SensorData.find({'p': 0, 's':2}):
#   if document['v'] >= s_id['yellow']['min'] and document['v'] <= s_id['yellow']['max']:
#     if document['v'] >= s_id['green']['min'] and document['v'] <= s_id['green']['max']:
#       green_counter+=1
#     else:
#       yellow_counter+=1
#   else:
#     red_counter+=1
#   pass

# print('LIGHT')
# print('RED: ' + str(red_counter))
# print('YELLOW: ' + str(yellow_counter))
# print('GREEN: ' + str(green_counter))

# s_id = ''
# for rang in ranges:
#   s_id = rang['settings'] if rang['sensor_id'] == 3 else s_id
# # print(s_id)

# yellow_counter = 0
# green_counter = 0
# red_counter = 0
# for document in db.SensorData.find({'p': 0, 's':3}):
#   if document['v'] >= s_id['yellow']['min'] and document['v'] <= s_id['yellow']['max']:
#     if document['v'] >= s_id['green']['min'] and document['v'] <= s_id['green']['max']:
#       green_counter+=1
#     else:
#       yellow_counter+=1
#   else:
#     red_counter+=1
#   pass

# print('MOISTURE')
# print('RED: ' + str(red_counter))
# print('YELLOW: ' + str(yellow_counter))
# print('GREEN: ' + str(green_counter))

# print(result.modified_count)

result = db.Plant.update_one(
  {'name': 'marta'},
  {
    '$unset': {
      'alive': 0
    },
    '$set': {
      'offline': [0, 12],
      'online': [6, 24],
      'sensor_status': [{
        "yellow" : ["light", "humidity", "temperature"],
        "red" : [],
        "green" : ["moisture"]
      }, {
        'current_counter': 12,
        'overall_counter': {
          'light': {
            'green': 450,
            'yellow': 2286,
            'red': 450
          },
          'temperature': {
            'green': 43,
            'yellow': 304,
            'red': 651
          },
          'humidity': {
            'green': 430,
            'yellow': 478,
            'red': 87
          },
          'moisture': {
            'green': 429,
            'yellow': 556,
            'red': 1806
          }
        }
      }]
    }
  }
  )
