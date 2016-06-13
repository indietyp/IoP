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

result = db.Plant.update_one(
  {'name': 'paul'},
  {'$set':{'responsible_id': 1}}
  )

print(result.modified_count)
