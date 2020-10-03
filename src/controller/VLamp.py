import math
import asyncio
import time

from src.controller import helpers, bulb
from src.controller.brightness import Brightness
from src.controller.temperature import ColorTemperature
from src.logger import log


class VLamp:
	def __init__(self, name):
		self.name: str = name
		self.lamp_access = False

		self.brightness = Brightness(set_brightness=self.set_brightness)
		self.color_temp = ColorTemperature(set_color_temp=self.set_color_temp)

	@helpers.run
	async def set_brightness(self):
		if self.lamp_access:
			if not bulb.is_on:
				log.debug(f'Lamp is off, turning on.')
				await bulb.turn_on()
				await bulb.update()

			turn_off = False
			if self.brightness.perceived == 0:
				self.brightness.perceived = 1
				turn_off = True

			log.debug(f'Changing brightness to {self.brightness.perceived}.')
			await bulb.set_brightness(self.brightness.actual)

			if turn_off:
				log.info(f'Brightness was set to 0, turning lamp off.')
				await asyncio.sleep(0.5)
				await bulb.turn_off()
		else:
			log.warning(f'{self.name} has no lamp access.')


	@helpers.run
	async def set_color_temp(self):
		if self.lamp_access:
			if not bulb.is_on:
				await bulb.turn_on()
				await bulb.update()

			log.info(f'Changing color temperature to {self.color_temp.kelvin}.')
			await bulb.set_color_temp(self.color_temp.kelvin)
		else:
			log.warning(f'{self.name} has no lamp access.')
		