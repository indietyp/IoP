from sensor_scripts.extensions.display import Display
from sensor_scripts.extensions.mailer import PlantMailer
from sensor_scripts.extensions.led.general import TrafficLight
from sensor_scripts.extensions.led.moisture_bar import MoistureBar


class ToolChainHardware(object):
  """docstring for ToolChainHardware"""

  def __init__(self):
    pass

  def execute_led_traffic_light(self, data):
    print('TrafficLight')
    TrafficLight.run()

  def execute_led_bar(self, data):
    print('MoistureBar')
    MoistureBar.run()

  def execute_display(self, data):
    print('Display')
    Display().set()

  def execute_water_pump(self, data):
    print('WATER_PUMP')

  def execute_mailer(self, data):
    print('mailer')
    PlantMailer().execute(data)

  def unicorn(self, data):
    print('PRAISE THE ALL MIGHTY UNICORN!')
