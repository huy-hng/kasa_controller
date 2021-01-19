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
		# TODO: only tweak speed since logic is reliable
		if self.lamp_access:
			if state:
				self.turn_on()

			else:
				self.turn_off()

	def turn_on(self, duration=0):
		if not self._on:
			asyncio.run(bulb.turn_on())
			# time.sleep(1)
			self.brightness.change(self.brightness.before_off_value, duration, 1)
			self.color_temp.change(self.color_temp.before_off_value, duration, 0)
			asyncio.run(bulb.update())
		self._on = True

	def turn_off(self, duration=0):
		if self._on:
			self.brightness.before_off_value = self.brightness.value
			self.color_temp.before_off_value = self.color_temp.value
			self.brightness.change(1, duration)
			self.color_temp.change(0, duration)
			time.sleep(0.5)
			while self.is_running:
				time.sleep(0.1)
			time.sleep(0.5)
			asyncio.run(bulb.turn_off())
			asyncio.run(bulb.update())
		self._on = False


	def set_brightness(self):
		turn_off = False
		if self.brightness.value == 0:
			self.brightness.value = 1
			turn_off = True
		elif not self.on:
			self._on = True
			time.sleep(3)

		if self.lamp_access:
			log.info(f'{self.name} changing brightness to {self.brightness.value}.')

			self.retry_on_fail(bulb.set_brightness, self.brightness.internal_value)

			if turn_off:
				log.info('Brightness was set to 0, turning lamp off.')
				time.sleep(1)
				asyncio.run(bulb.turn_off())
				self.on = False
		else:
			log.debug(f'{self.name} has no lamp access.')



	def set_color_temp(self):
		if self.lamp_access and self.on:
			log.info(f'{self.name} changing color temperature to {self.color_temp.internal_value}.')
			self.retry_on_fail(bulb.set_color_temp, self.color_temp.internal_value)
		else:
			log.debug(f'{self.name} has no lamp access.')



	def retry_on_fail(self, fn, val: int):
		for _ in range(12):
			try:
				asyncio.run(fn(val))
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
			'on': self._on,
			'brightness': self.brightness.value,
			'color_temp': self.color_temp.value,
			'is_running': self.is_running
		}