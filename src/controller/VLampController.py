import time

from src.controller.VLamp import VLamp
from src.logger import log

# pylint: disable=logging-fstring-interpolation

class VLampController:
	def __init__(self):
		self.nvl = VLamp(0, 'Normal VLamp')
		self.ovl = VLamp(1, 'Override VLamp')

		self.disengage()

	def override(self):
		log.info('Overriding nvl')

		self.ovl = VLamp(1, 'Override VLamp')
		self.ovl.brightness.perceived = self.nvl.brightness.perceived
		self.ovl.color_temp.kelvin = self.nvl.color_temp.kelvin

		self.nvl.lamp_access = False
		self.ovl.lamp_access = True
		self.active_vlamp = self.ovl


	def disengage(self, duration=1):
		""" disengages this vlamp and engages the vlamp given as param """
		log.info('Disengaging override, changing lamp access to nvl')

		self.ovl.on = self.nvl.on
		self.ovl.brightness.change(self.nvl.brightness.perceived, duration)
		self.ovl.color_temp.change(self.nvl.color_temp.percent, duration)

		time.sleep(0.5)

		while self.ovl.is_running:
			time.sleep(0.1)

		self.nvl.lamp_access = True
		self.ovl.lamp_access = False
		self.active_vlamp = self.nvl

		log.debug(f'running done')

		
	def is_normal_mode(self):
		return True if self.active_vlamp.id == 0 else False
