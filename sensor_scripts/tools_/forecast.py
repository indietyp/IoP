# FORECAST TODO
# insert in database -> roundup by 30
#   -> from last database-entry of sensor
#   -> do 48 times
#   -> for_time field + value + sensor + plant
# every time executes -> deletes every old entry

import datetime
import pandas
import numpy
import pygal
import pymongo
import pytz

from sklearn import preprocessing
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import LinearRegression

from bson import son
from multiprocessing import Pool
from pymongo import MongoClient
from bson import ObjectId

def simple_as_fuck_despiker(dataFrame):
  despiker = dataFrame.sort_values('v', ascending=False).head(n=25)

  for index, row in despiker.iterrows():
      dataFrame.drop(index, inplace=True)

  despiker = dataFrame.sort_values('v', ascending=True).head(n=25)

  for index, row in despiker.iterrows():
      dataFrame.drop(index, inplace=True)

  return dataFrame

def mape(ypred, ytrue):
  """ returns the mean absolute percentage error """
  idx = ytrue != 0.0
  return 100*numpy.mean(numpy.abs(ypred[idx]-ytrue[idx])/ytrue[idx])


def advanced_magic_regressor(dataFrame):
  columns = dataFrame.columns.tolist()
  columns = [c for c in columns if c not in ["s", "p", "_id"]]
  target = "v"
  dataFrame = simple_as_fuck_despiker(dataFrame)

  samplesCount = len(dataFrame.index)
  trainSet = dataFrame.head(n=samplesCount - 48)
  testSet = dataFrame.loc[~dataFrame.index.isin(trainSet.index)]

  model = ElasticNet()
  model.fit(trainSet[columns], trainSet[target])
  predictions = model.predict(testSet[columns])

  client = MongoClient('192.168.178.54')
  db = client.iop
  current_time = db.SensorData.find_one({'s': sensor[0:1], 'p': plant['abbreviation']}, sort=[("_id", pymongo.DESCENDING)])['_id'].generation_time
  if current_time.minute < 25:
    pass

# SLOWER ~ 18sek
def magic_data_framer(data):
  dataFrame = None
  for sample in data:
    if dataFrame is None:
      dataFrame = pandas.DataFrame(sample[1], index=[sample[0]])
    else:
      tmp_dataFrame = pandas.DataFrame(sample[1], index=[sample[0]])
      dataFrame = dataFrame.append(tmp_dataFrame)
  return dataFrame

# FASTER! ~ 0.05sek
def advanced_magic_data_framer(data):
  dataFrame = pandas.DataFrame({'v': data[0], 'year': data[1].astype(int), 'month': data[2].astype(int), 'day': data[3].astype(int), 'hour': data[4].astype(int), 'minute':data[5].astype(int), 'weekday':data[6].astype(int)}, index=data[7].astype(int))
  return dataFrame

def advanced_complicated_data_formatting():
  client = MongoClient('192.168.178.54')
  db = client.iop

  data = db.SensorData.find({'p': 1, 's':0}).sort([('_id', pymongo.ASCENDING)])

  constructedArray = numpy.array([[],[],[],[],[],[],[],[]])
  finishedData = None
  i = 0

  for sample in data:
    d = sample['_id'].generation_time

    constructedArray = numpy.append(constructedArray, [[sample['v']], [d.year], [d.month], [d.day], [d.hour], [d.minute], [d.weekday()], [i]], axis=1)
    i += 1

  finishedDataFrame = pandas.DataFrame()
  stuff = numpy.array_split(constructedArray, 6, axis=1)
  now = datetime.datetime.now()
  pool = Pool(processes=6)
  finishedDataFrame = finishedDataFrame.append(pool.map(advanced_magic_data_framer, stuff))
  advanced_magic_regressor(finishedDataFrame)

def complicated_data_formatting():
  client = MongoClient('192.168.178.54')
  db = client.iop

  data = db.SensorData.find({'p': 1, 's':0}).sort([('_id', pymongo.DESCENDING)])

  finishedData = None
  i = 0

  for sample in data:
    d = sample['_id'].generation_time
    sample['timestamp'] = (d - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

    if finishedData is None:
      finishedData = numpy.array([[i, sample]])
    else:
      finishedData = numpy.append(finishedData, [[i, sample]], axis=0)
    i += 1

  finishedDataFrame = pandas.DataFrame()
  stuff = numpy.array_split(finishedData, 6)
  pool = Pool(processes=6)
  finishedDataFrame = finishedDataFrame.append(pool.map(magic_data_framer, stuff))
  advanced_magic_regressor(finishedDataFrame)

# complicated_data_formatting()
advanced_complicated_data_formatting()
