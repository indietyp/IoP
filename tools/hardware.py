import logging
import tools.logger
from sensor_scripts.extensions.display import Display
from sensor_scripts.extensions.mailer import PlantMailer
from sensor_scripts.extensions.led.general import TrafficLight
from sensor_scripts.extensions.led.moisture_bar import MoistureBar
logger = logging.getLogger('sensor_scripts')


class ToolChainHardware(object):
  """docstring for ToolChainHardware"""

  def __init__(self):
    pass

  def execute_led_traffic_light(self, data):
    logger.info('executing traffic light')
    TrafficLight.run()

  def execute_led_bar(self, data):
    logger.info('executing moisture led bar')
    MoistureBar.run()

  def execute_display(self, data):
    logger.info('executing display')
    Display().set()

  def execute_water_pump(self, data):
    logger.info('executing water pump')

  def execute_mailer(self, data):
    logger.info('executing mailer')
    PlantMailer().execute(data)

  def unicorn(self, data):
    logger.critical('PRAISE THE ALL MIGHTY UNICORN!')
