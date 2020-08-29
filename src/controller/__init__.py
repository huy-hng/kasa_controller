from kasa import SmartBulb
bulb = SmartBulb('10.0.2.23')

stop_bright = False
stop_temp = False

running_bright = False
running_temp = False

SINGLE_CHANGE_DUR = 0.12

from src.controller.brightness import change_brightness
from src.controller.temperature import change_temperature

