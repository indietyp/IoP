from sensor_scripts.extensions.display import Display
from sensor_scripts.extensions.mailer import PlantMailer
# , mailer, water_pump
# from sensor_scripts.extensions.led import general, moisture_bar


class ToolChainHardware(object):
  """docstring for ToolChainHardware"""

  def __init__(self):
    pass

  def execute_led_traffic_light(self, data):
    print('TRAFFIC LIGHT')

  def execute_led_bar(self, data):
    print('LED_BAR')

  def execute_display(self, data):
    Display().set()

  def execute_water_pump(self, data):
    print('WATER_PUMP')

  def execute_mailer(self, data):
    PlantMailer().execute(data)

  def unicorn(self, data):
    print('PRAISE THE ALL MIGHTY UNICORN!')
