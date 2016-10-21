from models.sensor import SensorDangerMessage, SensorSatisfactionLevel
from models.sensor import SensorData
from models.plant import Person
from models.plant import MessagePreset
# from models.message import MessagePreset
from sensor_scripts.extensions.mailer import PlantMailer

# msg = MessagePreset()
# msg.name = 'en'
# msg.message = '[date] | [time (12h)]\n[plant] - [sensor]\n[current][unit]\n[warning_min] - [warning_max]'
# msg.default = True
# msg.save()
# wizard = Person.get(Person.wizard == True)
# wizard.preset = MessagePreset.get(MessagePreset.name == 'en')
# wizard.save()

msg = MessagePreset.get(MessagePreset.name == 'en')
msg.message = '[date] | [time (12h)]\n[plant] - [sensor]\nvalue: [current][unit]\nwarning: [warning_min] - [warning_max]'
msg.save()

messages = SensorData.select().order_by(SensorData.created_at.desc()).offset(10).limit(10)
mailer = PlantMailer()
mailer.format_messages(messages)


# t = SensorSatisfactionLevel.get(SensorSatisfactionLevel.label == 'threat')

# for data in SensorData.select().order_by(SensorData.created_at.desc()).limit(10):
#   message = SensorDangerMessage()
#   message.plant = data.plant
#   message.sensor = data.sensor
#   message.level = t
#   message.created_at = data.created_at

#   message.message = '---'
#   message.value = data.value

#   message.save()
