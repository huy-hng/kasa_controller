import asyncio
import time
from dataclasses import dataclass

import kasa

from src.controller import helpers, bulb
from src.controller.brightness import Brightness
from src.controller.temperature import ColorTemperature
from src.logger import log

# pylint: disable=logging-fstring-interpolation

class VLamp:
	def __init__(self, id_: str, name: str):
		self.name = name
		self.id = id_

		self._on = True
		self._lamp_access = False

		self.brightness = Brightness(set_val_fn=self.set_brightness)
		self.color_temp = ColorTemperature(set_val_fn=self.set_color_temp)
		self.sync()

	@property
	def lamp_access(self):
		return self._lamp_access

	@lamp_access.setter
	def lamp_access(self, val: bool):
		self._lamp_access = val
		if val and self.on:
			self.set_brightness()
			self.set_color_temp()


	def sync(self):
		asyncio.run(bulb.update())
		self.brightness.internal_value = bulb.brightness
		self.color_temp.internal_value = bulb.color_temp


	@property
	def on(self):
		return self._on

	@on.setter
	def on(self, state: bool):
		self._on = state
		# TODO: check if I can just use self.set_brightness and self.set_color_temp()
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
		turn_off = False
		if self.brightness.value == 0:
			self.brightness.value = 1
			turn_off = True

		if self.lamp_access:
			# if not bulb.is_on:
			# 	log.debug('Lamp is off, turning on.')
			# 	await bulb.turn_on()
			# 	await bulb.update()

			log.info(f'{self.name} changing brightness to {self.brightness.value}.')

			await self.retry_on_fail(bulb.set_brightness, self.brightness)

			if turn_off:
				log.info('Brightness was set to 0, turning lamp off.')
				await asyncio.sleep(0.5)
				await bulb.turn_off()
				self.on = False
		else:
			log.debug(f'{self.name} has no lamp access.')


	@helpers.run
	async def set_color_temp(self):
		if self.lamp_access:
			log.info(f'{self.name} changing color temperature to {self.color_temp.internal_value}.')
			await self.retry_on_fail(bulb.set_color_temp, self.color_temp)
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