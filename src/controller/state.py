import math
import asyncio
from dataclasses import dataclass

from src import controller
from src.controller import helpers
from src.controller.brightness import Brightness
from src.controller.temperature import ColorTemperature
from src.logger import log


@dataclass
class VLamp:
	SINGLE_CHANGE_DUR = 0.12

	lamp_access = False
	
	def __init__(self):
		self.brightness = Brightness(set_brightness=self.set_brightness)
		self.color_temp = ColorTemperature(set_color_temp=self.set_color_temp)


	def callback(self, location):
		# TODO: remove, since deprecated
		log.debug(f'callback called from {location}')
		if self.lamp_access:
			if location == 'brightness':
				asyncio.run(self.set_brightness())	
			if location == 'temperature':
				pass

	@helpers.run
	async def set_brightness(self):
		if not controller.bulb.is_on:
			await controller.bulb.turn_on()

		turn_off = False
		if self.brightness.perceived == 0:
			self.brightness.perceived = 1
			turn_off = True

		await controller.bulb.set_brightness(self.brightness.actual)

		if turn_off:
			log.info(f'Brightness was set to 0, turning lamp off.')
			await asyncio.sleep(0.2)
			await controller.bulb.turn_off()


	@helpers.run
	async def set_color_temp(value):
		if not controller.bulb.is_on:
			await controller.bulb.turn_on()

		log.debug(f'change temp to {value}')
		await controller.bulb.set_color_temp(self.color_temp.kelvin)
	