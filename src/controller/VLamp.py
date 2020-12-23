import asyncio
import time

import kasa

from src.controller import helpers, bulb
from src.controller.brightness import Brightness
from src.controller.temperature import ColorTemperature
from src.logger import log

# pylint: disable=logging-fstring-interpolation

class VLamp:
	def __init__(self, id_: int, name: str):
		self.id = id_
		self.name = name
		self.lamp_access = False
		self._on = True

		self.brightness = Brightness(set_brightness=self.set_brightness)
		self.color_temp = ColorTemperature(set_color_temp=self.set_color_temp)
		self.sync()


	def sync(self):
		self.brightness.internal_value = bulb.brightness
		self.color_temp.internal_value = bulb.color_temp


	@property
	def on(self):
		return self._on

	@on.setter
	def on(self, state: bool):
		self._on = state
		if self.lamp_access:
			if state:
				asyncio.run(bulb.turn_on())
				asyncio.run(bulb.set_brightness(self.brightness.internal_value))
				asyncio.run(bulb.set_color_temp(self.color_temp.internal_value))
				asyncio.run(bulb.update())
			else:
				asyncio.run(bulb.turn_off())
				asyncio.run(bulb.update())
				
		# self.set_brightness()
		# self.set_color_temp()


	@helpers.run
	async def set_brightness(self):
		if self.lamp_access:
			# if not bulb.is_on:
			# 	log.debug('Lamp is off, turning on.')
			# 	await bulb.turn_on()
			# 	await bulb.update()

			turn_off = False
			if self.brightness.value == 0:
				self.brightness.value = 1
				turn_off = True

			log.debug(f'Changing brightness to {self.brightness.value}.')

			await self.retry_on_fail(bulb.set_brightness, self.brightness)

			if turn_off:
				log.info('Brightness was set to 0, turning lamp off.')
				await asyncio.sleep(0.5)
				await bulb.turn_off()
		else:
			log.debug(f'{self.name} has no lamp access.')

	async def retry_on_fail(self, fn, val):
		for _ in range(12):
			try:
				await fn(val.internal_value)
				break
			except kasa.exceptions.SmartDeviceException as e:
				if 'Communication error' not in str(e):
					log.exception(e)
					break
				log.error('Cannot Change value due to communication error. Retrying...')
				time.sleep(5)
			except Exception as e:
				log.exception(e)
				val.should_stop = True
				break



	@helpers.run
	async def set_color_temp(self):
		if self.lamp_access:
			# if not bulb.is_on:
			# 	await bulb.turn_on()
			# 	await bulb.update()

			log.info(f'Changing color temperature to {self.color_temp.internal_value}.')
			await self.retry_on_fail(bulb.set_color_temp, self.color_temp)
		else:
			log.debug(f'{self.name} has no lamp access.')
		
	@property
	def is_running(self):
		if self.brightness.running or self.color_temp.running:
			return True
		return False


	@property
	def state(self):
		return {
			'id': self.id,
			'name': self.name,
			'lamp_access': self.lamp_access,
			'on': self.on,
			'brightness': self.brightness.value,
			'color_temp': self.color_temp.value,
			'is_running': self.is_running
		}