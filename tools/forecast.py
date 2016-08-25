import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import datetime
from models.sensor import SensorData
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
# from sklearn.tree import DecisionTreeRegressor

from sklearn.neighbors import RadiusNeighborsRegressor
# %matplotlib inline
# from matplotlib.pylab import rcParams
# rcParams['figure.figsize'] = 15, 6


class SensorDataForecast(object):
  def __init__(self):
    pass

  def test_stationarity(self, timeseries):

    # Determing rolling statistics
    rolmean = timeseries.rolling(center=False, window=12).mean()

  def learn(self, data):
    print('STARTED')
    sd = SensorData.select() \
                   .where(SensorData.plant == data['plant']) \
                   .where(SensorData.sensor == data['sensor']) \
                   .order_by(SensorData.created_at.asc())

    data = {}
    data['date'] = []
    data['value'] = []
    data['timestamp'] = []
    data['average'] = []

    data['year'] = []
    data['month'] = []
    data['day'] = []
    data['hour'] = []
    data['minute'] = []
    data['weekday'] = []

    for entry in sd:
      data['date'].append(entry.created_at)
      data['value'].append(entry.value)

    for date in data['date']:
      str_date = date.replace('+00:00', '')
      dt_date = datetime.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')

      data['year'].append(dt_date.year)
      data['month'].append(dt_date.month)
      data['day'].append(dt_date.day)
      data['hour'].append(dt_date.hour)
      data['minute'].append(dt_date.minute)

      data['weekday'].append(dt_date.date().isoweekday())
      data['timestamp'].append(dt_date.timestamp())
      last_datetime = dt_date

    future = {}
    future['date'] = []
    future['timestamp'] = []

    future['year'] = []
    future['month'] = []
    future['day'] = []
    future['hour'] = []
    future['minute'] = []
    future['weekday'] = []

    # for i in range(1, 95):
    for i in range(0, 2000):
      fu = last_datetime + datetime.timedelta(minutes=30)
      future['date'].append(fu)
      future['year'].append(fu.year)
      future['month'].append(fu.month)
      future['day'].append(fu.day)
      future['hour'].append(fu.hour)
      future['minute'].append(fu.minute)

      future['weekday'].append(fu.date().isoweekday())
      future['timestamp'].append(fu.timestamp())
      last_datetime = fu

    index = pd.DatetimeIndex(data['date'])
    time_series = pd.Series(data['value'], index=index)
    rolmean = time_series.rolling(center=False, window=12).mean()

    for entry in rolmean:
      data['average'].append(entry)

    data_frame = pd.DataFrame(data)
    data_frame = data_frame[data_frame.average.notnull()]

    columns = data_frame.columns.tolist()
    columns = [c for c in columns if c not in ['value', 'average', 'date']]

    # linear
    # model = ElasticNet()

    # quite good
    # model = RandomForestRegressor()

    # very good
    model = ExtraTreesRegressor()

    # model = RadiusNeighborsRegressor()
    model.fit(data_frame[columns].values,
              data_frame['average'].values)

    pred_data_frame = pd.DataFrame(future)
    predictions = model.predict(pred_data_frame[columns].values)

    index = pd.DatetimeIndex(data['date'])
    original = pd.Series(data['average'], index=index)

    index = pd.DatetimeIndex(future['date'])
    predicted = pd.Series(predictions, index=index)

    plt.plot(original, color='red')
    plt.plot(predicted, color='blue')
    plt.show()
    # print(time_series)
    # self.test_stationarity(time_series)


    # plt.plot(time_series)
    # plt.show()

  def run(self, data):
    self.learn(data)

if __name__ == '__main__':
  from models.plant import Plant
  from models.sensor import Sensor

  data = {}
  data['plant'] = Plant.get(Plant.name == 'marta')
  data['sensor'] = Sensor.get(Sensor.name == 'temperature')
  SensorDataForecast().run(data)
