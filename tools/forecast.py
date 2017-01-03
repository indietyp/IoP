import logging
import datetime
import numpy as np
import pandas as pd
import tools.logger
from settings.debug import GRAPH
from models.sensor import SensorData
from models.sensor import SensorDataPrediction
from sklearn.ensemble import ExtraTreesRegressor
logger = logging.getLogger('sensor_scripts')


class SensorDataForecast(object):
  def __init__(self):
    pass

  def show_graph(self, data_dates, data, prediction_dates, predictions):
    import matplotlib.pylab as plt

    index = pd.DatetimeIndex(data_dates)
    original = pd.Series(data, index=index)

    index = pd.DatetimeIndex(prediction_dates)
    predicted = pd.Series(predictions, index=index)

    plt.plot(original, color='red')
    plt.plot(predicted, color='blue')
    plt.show()

  def datetime_to_dict(self, array, field='date'):
    array['timestamp'] = []
    array['year'] = []
    array['month'] = []
    array['day'] = []
    array['hour'] = []
    array['minute'] = []
    array['weekday'] = []

    for d_time in array[field]:
      array['year'].append(d_time.year)
      array['month'].append(d_time.month)
      array['day'].append(d_time.day)
      array['hour'].append(d_time.hour)
      array['minute'].append(d_time.minute)

      array['weekday'].append(d_time.date().isoweekday())
      array['timestamp'].append(d_time.timestamp())

    return array

  def get_sensor_data(self, data):
    sd = SensorData.select() \
                   .where(SensorData.plant == data['plant']) \
                   .where(SensorData.sensor == data['sensor']) \
                   .order_by(SensorData.created_at.asc())

    return sd

  def simulated_data(self, data):
    sd = self.get_sensor_data(data)
    data_count = sd.count()

    if data_count == 0:
      other = {'plant': None, 'sensor': None}
      other['plant'] = Plant.select().where(Plant.localhost == False)[0]
      other['sensor'] = data['sensor']
      generated = []

      csd = self.get_sensor_data(other)
      data_count = csd.count()

      if data_count <= 1000:
        generated = self.predict(data, sd)
      else:
        import random
        start = random.randint(0, data_count - 1000)
        generated = self.predict(data, sd[start:start + 1000])

      for entry in sd:
        pass

      for entry in generated:
        pass

  def predict(self, data, sd):
    """ forecasting timebased sensor data
        INPUT dict
          plant - current plant object
          sensor - current sensor object

    """

    data = {}
    data['date'] = []
    data['value'] = []
    data['average'] = []

    future = {}
    future['date'] = []

    if len(sd) < 1000:
      logger.debug('amount of data: ' + len(sd))
      logger.error('not enough samples')
      return []

    between = datetime.datetime.now()
    for entry in sd:
      created_at = entry.created_at
      if isinstance(created_at, str):
        str_entry = created_at.replace('+00:00', '')
        dt_date = datetime.datetime.strptime(str_entry, '%Y-%m-%d %H:%M:%S')
      else:
        # print(type(created_at))
        dt_date = created_at
      data['date'].append(dt_date)

      data['value'].append(entry.value)

    last_datetime = data['date'][-1]
    logger.debug('(106-120) time elapsed: {}'.format(datetime.datetime.now() - between))

    cap = int(len(data['date']) / 100 * 10)
    if cap > 144:
      cap = 144

    for i in range(0, cap):
      current = last_datetime + datetime.timedelta(minutes=30)
      future['date'].append(current)
      last_datetime = current

    between = datetime.datetime.now()
    data = self.datetime_to_dict(data)
    future = self.datetime_to_dict(future)
    logger.debug('(131-134) time elapsed: {}'.format(datetime.datetime.now() - between))

    between = datetime.datetime.now()
    index = pd.DatetimeIndex(data['date'])
    time_series = pd.Series(data['value'], index=index)
    rolmean = time_series.rolling(center=False, window=12).mean()
    logger.debug('(136-140) time elapsed: {}'.format(datetime.datetime.now() - between))

    between = datetime.datetime.now()
    for entry in rolmean:
      data['average'].append(entry)

    data_frame = pd.DataFrame(data)
    data_frame = data_frame[data_frame.average.notnull()]

    columns = data_frame.columns.tolist()
    columns = [c for c in columns if c not in ['value', 'average', 'date']]
    logger.debug('(142-151) time elapsed: {}'.format(datetime.datetime.now() - between))

    between = datetime.datetime.now()
    model = ExtraTreesRegressor()
    model.fit(data_frame[columns].values,
              data_frame['average'].values)

    pred_data_frame = pd.DataFrame(future)
    predictions = model.predict(pred_data_frame[columns].values)
    logger.debug('(153-160) time elapsed: {}'.format(datetime.datetime.now() - between))

    between = datetime.datetime.now()
    future['prediction'] = []
    for prediction in predictions:
      future['prediction'].append(prediction)
    logger.debug('(162-166) time elapsed: {}'.format(datetime.datetime.now() - between))

    if GRAPH is True:
      self.show_graph(data['date'], data['average'], future['date'], predictions)

    return future

  def insert_database(self, data):
    deletion = datetime.datetime.now()
    SensorDataPrediction.delete().where(SensorDataPrediction.plant == data['plant']) \
                                 .where(SensorDataPrediction.sensor == data['sensor']) \
                                 .execute()
    logger.debug('elapsed time deleting: {}'.format(datetime.datetime.now() - deletion))

    time_insert = datetime.datetime.now()
    prepared = []
    for key, prediction in enumerate(data['prediction']['prediction']):
      prepared.append({'plant': data['plant'],
                       'sensor': data['sensor'],
                       'value': prediction,
                       'time': data['prediction']['date'][key]})

      # entry = SensorDataPrediction()
      # entry.plant = data['plant']
      # entry.sensor = data['sensor']
      # entry.value = prediction
      # entry.time = data['prediction']['date'][key]
      # entry.save()
    from models.plant import db

    with db.atomic():
      for idx in range(0, len(prepared), 100):
        SensorDataPrediction.insert_many(prepared[idx:idx + 100]).execute()
      # SensorDataPrediction.insert_many(prepared).execute()
    logger.debug('insert time elapsed: {}'.format(datetime.datetime.now() - time_insert))
    logger.debug('overall time elapsed: {}'.format(datetime.datetime.now() - deletion))

  def run(self, data):
    sd = self.get_sensor_data(data)
    if sd.count() > 1000:
      data['prediction'] = self.predict(data, sd)
      self.insert_database(data)


if __name__ == '__main__':
  from models.plant import Plant
  from models.sensor import Sensor

  data = {}
  data['plant'] = Plant.get(Plant.name == 'marta')
  data['sensor'] = Sensor.get(Sensor.name == 'light')
  print(data['sensor'])
  SensorDataForecast().run(data)
  print('done')
  data['sensor'] = Sensor.get(Sensor.name == 'humidity')
  SensorDataForecast().run(data)
  print('done')
  data['sensor'] = Sensor.get(Sensor.name == 'moisture')
  SensorDataForecast().run(data)
