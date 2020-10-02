import math
import time
import asyncio
import typing
from dataclasses import dataclass

from src.controller import helpers, SINGLE_CHANGE_DUR
from src.logger import log


@dataclass
class Brightness:
	_actual = 0
	_perceived = 0
	set_brightness: typing.Callable

	running = False
	should_stop = False
	

	@property
	def actual(self):
		return self._actual

	@property
	def perceived(self):
		return self._perceived

	@actual.setter
	def actual(self, val):
		val = self.check_valid_range(val)

		self._actual = val
		self._perceived = round(math.sqrt(val*100))
		self.set_brightness()

	@perceived.setter
	def perceived(self, val):
		val = self.check_valid_range(val)

		self._perceived = val
		self._actual = round((val ** 2) / 100) 
		self.set_brightness()


	@staticmethod
	def check_valid_range(val):
		if val < 0:
			val = 0
		elif val > 100:
			val = 100
		return val
			

	
	@helpers.thread
	def change_brightness(self, target_value: int, duration: int, start_value: int=None):
		log.info(f'changing brightness to {target_value}, with duration of {duration}')
		self.running = True

		if duration==0:
			# change immediately
			self.perceived = target_value
			self.running = False
			return
		elif start_value is not None:
			self.perceived = start_value
			
		self.transition_bright(target_value, duration)
		self.running = False


	def transition_bright(self, target_value: int, duration: int):
		log.debug(f'transitioning')

		diff = target_value - self.perceived

		if diff == 0: return # return when theres no change to make

		amount_of_steps, step_size = self.get_steps(duration, diff)
		single_sleep_dur = helpers.calc_sleep_dur(duration, amount_of_steps)

		steps = helpers.calc_steps(diff, amount_of_steps, step_size, self.perceived, target_value)

		log.info(f'{steps=}')
		log.info(f'{self.perceived=} {target_value=} {amount_of_steps=} {single_sleep_dur=}')
		
		# transition
		for step in steps:
			self.perceived = step

			time.sleep(single_sleep_dur)

			if self.should_stop:
				self.should_stop = False
				break
		

	@staticmethod
	def get_steps(duration, diff):
		step_size = (diff * SINGLE_CHANGE_DUR) / (duration)
		
		if abs(step_size) < 2:
			step_size = 2 if step_size > 0 else -2
		elif step_size < 0:
			step_size = math.floor(step_size)
		else:
			step_size = math.ceil(step_size)

		# log.debug(f'{step_size=}')
		amount_of_steps = math.ceil(diff / step_size)
		return amount_of_steps, step_size
