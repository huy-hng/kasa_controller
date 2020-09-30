from kasa import SmartBulb
from src.controller.state import VLamp
bulb = SmartBulb('10.0.2.23')

vl = VLamp()

from src.controller.brightness import change_brightness
from src.controller.temperature import change_temperature

