import datetime
from tools.mail import NotificationMailer
from models.sensor import SensorSatisfactionLevel
from models.sensor import SensorSatisfactionValue, SensorDangerMessage


class PlantMailer(object):
  def __init__(self):
    pass

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
        for part in unsent:
          s = SensorSatisfactionLevel.get(SensorSatisfactionLevel.label == 'cautioning')
          c = SensorSatisfactionValue.select()\
                                     .where(SensorSatisfactionValue.level == s)\
                                     .where(SensorSatisfactionValue.plant == data['plant'])\
                                     .where(SensorSatisfactionValue.sensor == part.sensor)[0]
          message += """
                      {0}
                      Sensor: {1}
                      Plant: {5}
                      Level: threat
                      current: {2}{6}
                      cautioning at {3}{6} to {4}{6}


                     """.format(part.created_at.strftime('%H:%M'),
                                part.sensor.name,
                                round(part.value, 2),
                                c.min_value,
                                c.max_value,
                                data['plant'].name,
                                part.sensor.unit)

        self.send_message(data, message)

        for part in unsent:
          part.sent = True
          part.sent_time = now
          part.save()

    return True


if __name__ == "__main__":
  pass
