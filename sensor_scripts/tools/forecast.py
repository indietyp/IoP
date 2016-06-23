import datetime
import pandas
import numpy
import pygal
import pymongo
import pytz

from sklearn import preprocessing
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import ElasticNet

from bson import son
from multiprocessing import Pool
from pymongo import MongoClient
from bson import ObjectId



def  magic_regressor(sensor):
  client = MongoClient('192.168.178.54')
  db = client.iop
  # plant = db.Plant.find_one()['plant_id']
  plant = 1

  sensorData = db.SensorData.find({'p': plant, 's':0}).sort([('_id', pymongo.DESCENDING)])

  # now = datetime.datetime.now()
  # dataFrame = pandas.DataFrame()
  # for field in sensorData:
  #   d = field['_id'].generation_time
  #   field['value'] = field['v']
  #   field['hour'] = d.hour
  #   field['minute'] = d.minute
  #   field['weekday'] = d.weekday()
  #   field['day'] = d.day
  #   field['month'] = d.month
  #   field['year'] = d.year

  #   dataFrame = dataFrame.append(field, ignore_index=True)

  #   # if dataFrame is None:
  #   #   dataFrame = pandas.DataFrame(field, index=[0])
  #   # else:
  #   #   tmp_dataFrame = pandas.DataFrame(field, index=[0])
  #   #   dataFrame = dataFrame.append(tmp_dataFrame, ignore_index=True)

  # print datetime.datetime.now() - now

  now = datetime.datetime.now()
  dataFrame = None
  for field in sensorData:
    d = field['_id'].generation_time
    field['value'] = field['v']
    field['hour'] = d.hour
    field['minute'] = d.minute
    field['weekday'] = d.weekday()
    field['day'] = d.day
    field['month'] = d.month
    field['year'] = d.year

    # dataFrame = dataFrame.append(field, ignore_index=True)

    if dataFrame is None:
      dataFrame = pandas.DataFrame(field, index=[0])
    else:
      tmp_dataFrame = pandas.DataFrame(field, index=[0])
      dataFrame = dataFrame.append(tmp_dataFrame, ignore_index=True)

  print datetime.datetime.now() - now


  columns = dataFrame.columns.tolist()
  columns = [c for c in columns if c not in ["s", "p", "_id"]]
  target = "value"
  print colums
  despiker = dataFrame.sort_values('v', ascending=False).head(n=25)

  for index, row in despiker.iterrows():
      dataFrame.drop(index, inplace=True)

  despiker = dataFrame.sort_values('v', ascending=True).head(n=25)

  for index, row in despiker.iterrows():
      dataFrame.drop(index, inplace=True)

  samplesCount = len(dataFrame.index)

  trainSet = dataFrame.sample(n=samplesCount - 48, random_state=1)
  testSet = dataFrame.loc[~dataFrame.index.isin(trainSet.index)]

  # print testSet
  # print trainSet

def simple_as_fuck_despiker(dataFrame):
  despiker = dataFrame.sort_values('v', ascending=False).head(n=25)

  for index, row in despiker.iterrows():
      dataFrame.drop(index, inplace=True)

  despiker = dataFrame.sort_values('v', ascending=True).head(n=25)

  for index, row in despiker.iterrows():
      dataFrame.drop(index, inplace=True)

  return dataFrame

def advanced_magic_regressor(dataFrame):
  columns = dataFrame.columns.tolist()
  columns = [c for c in columns if c not in ["s", "p", "_id"]]
  target = "v"
  print columns
  dataFrame = simple_as_fuck_despiker(dataFrame)

  samplesCount = len(dataFrame.index)
  trainSet = dataFrame.sample(n=samplesCount - 48, random_state=1)
  testSet = dataFrame.loc[~dataFrame.index.isin(trainSet.index)]

  model = ElasticNet()
  model.fit(trainSet[columns], trainSet[target])
  predictions = model.predict(testSet[columns])

  print predictions

def magic_data_framer(data):
  dataFrame = None
  for sample in data:
    if dataFrame is None:
      dataFrame = pandas.DataFrame(sample[1], index=[sample[0]])
    else:
      tmp_dataFrame = pandas.DataFrame(sample[1], index=[sample[0]])
      dataFrame = dataFrame.append(tmp_dataFrame)
  return dataFrame

def complicated_data_formatting():
  client = MongoClient('192.168.178.54')
  db = client.iop
  # plant = db.Plant.find_one()['plant_id']

  data = db.SensorData.find({'p': 1, 's':0}).sort([('_id', pymongo.DESCENDING)])

  finishedData = None
  i = 0

  for sample in data:
    d = sample['_id'].generation_time
    # sample['value'] = sample['v']
    # sample['hour'] = d.hour
    # sample['minute'] = d.minute
    # sample['weekday'] = d.weekday()
    # sample['day'] = d.day
    # sample['month'] = d.month
    # sample['year'] = d.year
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

complicated_data_formatting()
