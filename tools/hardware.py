from sensor_scripts.extensions.display import Display
from sensor_scripts.extensions.mailer import Mailer
# , mailer, water_pump
# from sensor_scripts.extensions.led import general, moisture_bar


class ToolChainHardware(object):
  """docstring for ToolChainHardware"""
  def __init__(self):
    pass

  def execute_led_traffic_light(self):
    print('TRAFFIC LIGHT')

  def execute_led_bar(self):
    print('LED_BAR')

  def execute_display(self):
    Display().set()

  def execute_water_pump(self):
    print('WATER_PUMP')

  def execute_mailer(self):
    print('MAILER')

  def unicorn(self):
    print('PRAISE THE ALL MIGHTY UNICORN!')
