import math
import time
from dataclasses import dataclass

from src.controller import helpers, SINGLE_CHANGE_DUR
from src.logger import log

from old_code.parent_value_class import Parent

# pylint: disable=logging-fstring-interpolation
# pylint: disable=multiple-statements

class Brightness(Parent):
	def __init__(self, set_val_fn):
		self.internal_valid_range = (0, 100)
		self.external_valid_range = (0, 100)
		self.set_val_fn = set_val_fn


	@staticmethod
	def convert_to_external(internal: int) -> int:
		return round( ((23526*internal)**(1/3)) - 33 )

	@staticmethod
	def convert_to_internal(external: int) -> int:
		return round(( (external + 33)**3 ) / 23526)

	def _transition(self, target_value: int, duration: int):
		log.info(f'Transitioning to {target_value} with duration of {duration}')

		diff = target_value - self.value

		if diff == 0: return # return when theres no change to make

		amount_of_steps, step_size = self.get_steps(duration, diff)
		single_sleep_dur = helpers.calc_sleep_dur(duration, amount_of_steps)

		steps = helpers.calc_steps(diff, amount_of_steps, step_size, self.value, target_value)

		log.info(f'{steps=}')
		log.info(f'{self.value=} {target_value=} {amount_of_steps=} {single_sleep_dur=}')
		
		# transition

		for step in steps:
			self.value = step
			self.set_val_fn()

			time.sleep(single_sleep_dur)

			if self.should_stop:
				self.should_stop = False
				log.info('Stopping Brightness change.')
				break

		log.debug('Done transitioning.')


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
