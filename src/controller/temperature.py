import math
import time
from dataclasses import dataclass

from src.controller import helpers, SINGLE_CHANGE_DUR
from src.logger import log

from src.controller.parent_value_class import Parent


# pylint: disable=logging-fstring-interpolation

@dataclass
class ColorTemperature(Parent):
	def __init__(self, set_val_fn):
		self.internal_valid_range = (2700, 6500)
		self.external_valid_range = (0, 100)
		self.set_val_fn = set_val_fn


	@staticmethod
	def convert_to_external(internal) -> int:
		return int((internal - 2700) / 38)

	@staticmethod
	def convert_to_internal(external) -> int:
		return int(38 * external + 2700)



	def transition(self, target_value: int, duration:int):
		target_kelvin = self.convert_to_internal(target_value)

		diff = target_kelvin - self.internal_value

		if diff == 0: return # return when theres no change to make

		#region calc step_size
		step_size = (diff * SINGLE_CHANGE_DUR) / duration

		if abs(step_size) < 100:
			step_size = 100 if step_size > 0 else -100

		step_size = self.round_to_nearest_100(step_size)
		#endregion

		amount_of_steps = math.ceil(diff / step_size)
		single_sleep_dur = helpers.calc_sleep_dur(duration, amount_of_steps)

		steps = helpers.calc_steps(diff, amount_of_steps, step_size, self.internal_value, target_kelvin)

		log.debug(f'{step_size=}')
		log.info(f'{self.internal_value=} {target_kelvin=} {duration=} {amount_of_steps=} {single_sleep_dur=}')


		# transition
		for step in steps:
			self.internal_value = step
			self.set_val_fn()

			time.sleep(single_sleep_dur)

			if self.should_stop:
				self.should_stop = False
				break


	@staticmethod
	def round_to_nearest_100(x, base=100):
		return int(base * round(float(x)/base))

	def wait_for_stop(self):
		if self.running:
			self.should_stop = True

		while self.running:
			time.sleep(0.1)