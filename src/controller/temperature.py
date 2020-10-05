import math
import typing
import time
import asyncio
from dataclasses import dataclass

from src.controller import helpers, SINGLE_CHANGE_DUR, bulb
from src.logger import log

# pylint: disable=logging-fstring-interpolation

@dataclass
class ColorTemperature:
	_percent = 0
	_kelvin = 2700
	set_color_temp: typing.Callable
	
	running = False
	should_stop = False


	@property
	def percent(self):
		return self._percent

	@property
	def kelvin(self):
		return self._kelvin

	@percent.setter
	def percent(self, val):
		if val < 0: val = 0
		elif val > 100: val = 100

		self._percent = val
		self._kelvin = self.convert_to_kelvin(val)
		self.set_color_temp()

	@kelvin.setter
	def kelvin(self, val):
		if val < 2700: val = 2700
		elif val > 6500: val = 6500

		self._percent = self.convert_to_percent(val)
		self._kelvin = val
		self.set_color_temp()

	@staticmethod
	def convert_to_percent(kelvin) -> int:
		return int((kelvin - 2700) / 38)

	@staticmethod
	def convert_to_kelvin(percent) -> int:
		return int(38 * percent + 2700)


	@helpers.thread
	def change(self, target_value: int, duration: int, start_value: int=None):
		log.info(f'changing color temp to {target_value}, with duration of {duration}')
		self.running = True
		asyncio.run(bulb.update())

		if duration==0:
			self.percent = target_value
			self.running = False
			return
		elif start_value is not None:
			self.percent = target_value
			time.sleep(1)

		self.transition(target_value, duration)
		self.running = False


	def transition(self, target_percent: int, duration:int):
		target_kelvin = self.convert_to_kelvin(target_percent)

		diff = target_kelvin - self.kelvin

		if diff == 0: return # return when theres no change to make

		#region calc step_size
		step_size = (diff * SINGLE_CHANGE_DUR) / duration

		if abs(step_size) < 100:
			step_size = 100 if step_size > 0 else -100

		step_size = self.round_to_nearest_100(step_size)
		#endregion

		amount_of_steps = math.ceil(diff / step_size)
		single_sleep_dur = helpers.calc_sleep_dur(duration, amount_of_steps)

		steps = helpers.calc_steps(diff, amount_of_steps, step_size, self.kelvin, target_kelvin)

		log.debug(f'{step_size=}')
		log.info(f'{self.kelvin=} {target_kelvin=} {duration=} {amount_of_steps=} {single_sleep_dur=}')


		# transition
		for step in steps:
			self.kelvin = step

			time.sleep(single_sleep_dur)

			if self.should_stop:
				self.should_stop = False
				break


	@staticmethod
	def round_to_nearest_100(x, base=100):
		return int(base * round(float(x)/base))
