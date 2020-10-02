import math
import typing
import time
from dataclasses import dataclass

from src.controller import helpers, SINGLE_CHANGE_DUR
from src.logger import log


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
		log.debug(f'{val=}')

		self._percent = val
		self._kelvin = self.convert_to_kelvin(val)

	@kelvin.setter
	def kelvin(self, val):
		if val < 2700: val = 2700
		elif val > 6500: val = 6500
		log.debug(f'{val=}')

		self._percent = self.convert_to_percent(val)
		self._kelvin = val

	@staticmethod
	def convert_to_percent(kelvin):
		return (kelvin - 2700) / 38

	@staticmethod
	def convert_to_kelvin(percent):
		return 38 * percent + 2700


	# @helpers.thread
	def change_temperature(self, target_value: int, duration: int, start_value: int=None):
		self.running = True

		log.warning('')

		if duration==0:
			self.percent = target_value
			self.running = False
			return
		elif start_value is not None:
			self.percent = target_value

		self.transition_color_temp(target_value, duration)
		self.running = False


	def transition_color_temp(self, target_percent: int, duration:int):
		target_kelvin = self.convert_to_kelvin(target_percent)
		diff, cond = helpers.get_diff(self.kelvin, target_kelvin)

		if diff == 0: return # return when theres no change to make

		#region calc step_size
		step_size = (diff * SINGLE_CHANGE_DUR) / duration

		if abs(step_size) < 100:
			step_size = 100 if step_size > 0 else -100

		step_size = self.round_to_nearest_100(step_size)
		log.info(f'{step_size=}')
		#endregion

		amount_of_steps = math.ceil(diff / step_size)
		single_sleep_dur = helpers.calc_sleep_dur(duration, amount_of_steps)

		log.debug(f'{step_size=}')
		log.info(f'{self.kelvin=} {target_kelvin=} {duration=} {amount_of_steps=} {single_sleep_dur=}')

		# transition
		while cond(self.kelvin):
			self.kelvin += step_size

			if not cond(self.kelvin):
				# check that self.kelvin doesnt overshoot target_kelvin
				self.kelvin = target_kelvin

			if self.should_stop:
				self.should_stop = False
				break

			time.sleep(single_sleep_dur)


	@staticmethod
	def round_to_nearest_100(x, base=100):
		return int(base * round(float(x)/base))
