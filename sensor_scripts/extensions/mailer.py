import datetime
from tools.mail import NotificationMailer
from models.sensor import SensorSatisfactionLevel
from models.sensor import SensorSatisfactionValue, SensorDangerMessage
from models.message import MessagePreset
from tools.main import VariousTools


class PlantMailer(object):
  def __init__(self):
    pass

  def format_messages(self, messages):
    output = ''

    for part in messages:
      preset = part.plant.person.preset

      created_at = part.created_at.replace('+00:00', '')
      try:
        created_at = datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
      except:
        created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f")


      s = SensorSatisfactionLevel.get(SensorSatisfactionLevel.label == 'cautioning')
      c = SensorSatisfactionValue.select()\
                                 .where(SensorSatisfactionValue.level == s)\
                                 .where(SensorSatisfactionValue.plant == part.plant)\
                                 .where(SensorSatisfactionValue.sensor == part.sensor)[0]

      s = SensorSatisfactionLevel.get(SensorSatisfactionLevel.label == 'optimum')
      o = SensorSatisfactionValue.select()\
                                 .where(SensorSatisfactionValue.level == s)\
                                 .where(SensorSatisfactionValue.plant == part.plant)\
                                 .where(SensorSatisfactionValue.sensor == part.sensor)[0]

      tmp = preset.message

      for r in [['[sensor]', part.sensor.name],
                ['[plant]', part.plant.name],
                ['[date]', created_at.strftime('%d. %b')],
                ['[current]', str(part.value)],
                ['[time (12h)]', created_at.strftime('%I:%M %p')],
                ['[time (24h)]', created_at.strftime('%H:%M')],
                ['[name]', part.plant.person.name],
                ['[email]', part.plant.person.email],
                ['[ideal_min]', str(o.min_value)],
                ['[ideal_max]', str(o.max_value)],
                ['[warning_min]', str(c.min_value)],
                ['[warning_max]', str(c.max_value)],
                ['[unit]', part.sensor.unit]]:

        tmp = tmp.replace(r[0], r[1])

      # print(tmp)
      output += tmp + '\n\n'

    print(output)




  def send_message(self, data, message):
    mailer_instance = NotificationMailer()
    mailer, account = mailer_instance.get_notification_mailer()

    author = account[0].account
    subject = 'scheduled threat report'
    to = data['plant'].person.email

    mailer_instance.send_message(mailer, author, account[1], to, subject, message)

    return True

  def execute(self, data):
    """ data
          sensor - sensor object
          plant - plant object
          value - current value
          satisfaction - current satisfaction
    """
    result = VariousTools.offline_check('notification', hardware=False)
    if result is True:

      if data['satisfaction'].level.label == 'threat':
        message = SensorDangerMessage()
        message.plant = data['plant']
        message.sensor = data['sensor']
        message.level = data['satisfaction'].level

        message.message = '---'
        message.value = data['value']

        message.save()

      now = datetime.datetime.now()

      se = SensorDangerMessage.select()\
                              .where(SensorDangerMessage.sent == True)\
                              .where(SensorDangerMessage.plant == data['plant'])\
                              .order_by(SensorDangerMessage.created_at.desc())
      sent = se

      us = SensorDangerMessage.select()\
                              .where(SensorDangerMessage.sent == False)\
                              .where(SensorDangerMessage.plant == data['plant'])\
                              .order_by(SensorDangerMessage.created_at.asc())
      unsent = us

      if unsent.count() != 0 and (now - unsent[0].created_at).seconds > 5 * 60:

        interval = data['plant'].interval * 60 * 60
        if sent.count() == 0 or (now - se[0].created_at).seconds >= interval:
          message = ''
          # for part in unsent:
          #   s = SensorSatisfactionLevel.get(SensorSatisfactionLevel.label == 'cautioning')
          #   c = SensorSatisfactionValue.select()\
          #                              .where(SensorSatisfactionValue.level == s)\
          #                              .where(SensorSatisfactionValue.plant == data['plant'])\
          #                              .where(SensorSatisfactionValue.sensor == part.sensor)[0]
          #   message +=
          #               {0}
          #               Sensor: {1}
          #               Plant: {5}
          #               Level: threat
          #               current: {2}{6}
          #               cautioning at {3}{6} to {4}{6}


          #              .format(part.created_at.strftime('%H:%M'),
          #                         part.sensor.name,
          #                         round(part.value, 2),
          #                         c.min_value,
          #                         c.max_value,
          #                         data['plant'].name,
          #                         part.sensor.unit)

          message += self.format_messages(data, unsent)

          self.send_message(data, message)

          for part in unsent:
            part.sent = True
            part.sent_time = now
            part.save()

      return True
    else:
      return False


if __name__ == "__main__":
  pass
