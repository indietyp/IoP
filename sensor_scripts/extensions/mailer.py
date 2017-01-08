import datetime
from tools.mail import NotificationMailer
from models.sensor import SensorSatisfactionLevel
from models.plant import Plant, Person
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

      if isinstance(part.created_at, str):
        created_at = part.created_at.replace('+00:00', '')
        try:
          created_at = datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        except:
          created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f")
      else:
        created_at = part.created_at


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

      output += tmp + '\n\n'

    return output

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
    local = Plant.get(Plant.localhost == True)
    online = VariousTools.offline_check('notification', hardware=False)
    if online and local.host:
      latest = SensorDangerMessage.select()\
                                  .where(SensorDangerMessage.sent == True) \
                                  .order_by(SensorDangerMessage.created_at.desc()) \
                                  .limit(1) \
                                  .dicts()

      latest = list(latest)

      now = datetime.datetime.now()
      interval = data['plant'].interval * 60 * 60
      if len(latest) == 0 or (now - latest[0]['created_at']).seconds >= interval:
        for person in Person.select():
          us = SensorDangerMessage.select() \
                                  .where(SensorDangerMessage.sent == False) \
                                  .where(SensorDangerMessage.plant << Plant.select().where(Plant.person == person)) \
                                  .order_by(SensorDangerMessage.created_at.asc())
          unsent = us

          if unsent.count() != 0:
            for partial in unsent:
              partial.sent = True
              partial.sent_time = now
              partial.save()

            message = ''
            message += self.format_messages(unsent)
            self.send_message(data, message)

      return True
    else:
      return False


if __name__ == "__main__":
  pass
