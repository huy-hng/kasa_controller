import math
import asyncio
from dataclasses import dataclass

from kasa import SmartBulb

from src.logger import log
from src.helpers import run_parallel, run_sequential

@dataclass
class BulbController(SmartBulb):
	prev_state = {
		'brightness': 0,
		'color_temp': 0
	}
	SINGLE_CHANGE_DUR = 0.12
	min_color_temp = 2700
	max_color_temp = 6000
	color_temp_factor = (max_color_temp - min_color_temp) / 100

	def __init__(self, ip: str):
		super().__init__(ip)
		

	async def turn_on(self, duration=None):
		await super().turn_on()
		await asyncio.sleep(2)
		await run_parallel(
			self.set_brightness(self.prev_state['brightness'], duration),
			self.set_color_temp(self.prev_state['color_temp'], duration)
		)

	async def turn_off(self, duration=None):
		await self.update()
		self.prev_state['brightness'] = self.lin_to_log(self.brightness)
		self.prev_state['color_temp'] = self.kelvin_to_percentage(self.color_temp)

		await run_sequential(
			run_parallel(
				self.set_brightness(0, duration),
				self.set_color_temp(0, duration)
			),
			asyncio.sleep(1),
			super().turn_off()
		)
		

	#region brightness
	async def set_brightness(self, val: int, transition: int=1000):
		adjusted = self.log_to_lin(val)
		log.debug(f'Setting brightness to {adjusted}')
		await super().set_brightness(adjusted, transition=transition)

	async def set_raw_brightness(self, val: int, transition: int=1000):
		""" Set brightness without any adjustments. That means both
				linear and logarithmic values can be used. """
		await super().set_brightness(val, transition=transition)

	async def transition_brightness(self, target_value: int, duration: int):
		log.info(f'Transitioning to {target_value} with duration of {duration}')

		await self.update()
		diff = target_value - self.lin_to_log(self.brightness)

		if diff == 0: return # return when theres no change to make

		step_size = self.get_step_size(duration, diff)
		amount_of_steps = math.ceil(diff / step_size)

		single_sleep_dur = self.calc_sleep_dur(duration, amount_of_steps)
		# steps = self.calc_steps(diff, amount_of_steps, step_size, target_value)

		curr_val = self.lin_to_log(self.brightness)
		steps = range(curr_val, target_value, step_size)
		for step in steps:
			await self.set_brightness(step)

			await asyncio.sleep(single_sleep_dur)

			# if self.should_stop:
			# 	self.should_stop = False
			# 	log.info('Stopping Brightness change.')
			# 	break

		log.debug('Done transitioning.')


	#region brightness helpers
	@staticmethod
	def lin_to_log(internal: int) -> int:
		return round(( (23526*internal) ** (1/3) ) - 33)


	@staticmethod
	def log_to_lin(external: int) -> int:
		return round(( (external + 33) ** 3 ) / 23526)


	def calc_steps(self, diff, amount_of_steps, step_size, target):
		step_dir = True if diff > 0 else False

		steps: list[int] = []
		curr_val = self.brightness
		for _ in range(amount_of_steps):
			curr_val += step_size
			if curr_val > target and step_dir or curr_val < target and not step_dir:
				curr_val = target

			steps.append(curr_val)

		return steps


	def calc_sleep_dur(self, duration, amount_of_steps):
		expected_change_dur = self.SINGLE_CHANGE_DUR * amount_of_steps
		sleep_dur = duration - expected_change_dur

		sleep_dur = max(0, sleep_dur)

		return sleep_dur / amount_of_steps


	def get_step_size(self, duration, diff):
		step_size = (diff * self.SINGLE_CHANGE_DUR) / (duration)
		
		if abs(step_size) < 2:
			step_size = 2 if step_size > 0 else -2
		elif step_size < 0:
			step_size = math.floor(step_size)
		else:
			step_size = math.ceil(step_size)

		return step_size
	#endregion brightness helpers
	#endregion brightness


	#region color_temp
	async def set_color_temp(self, temp: int, transition: int=1000):
		"""
		Set the color temperature of the device in percentage.

		:param int temp: The new color temperature, in percent
		:param int transition: transition in milliseconds.
		"""

		adjusted = self.percentage_to_kelvin(temp)
		await super().set_color_temp(adjusted, transition=transition)

	async def transition_color_temp(self, target_value: int, duration):
		self.set_color_temp(target_value, duration * 1000)


	#region color_temp helpers
	def kelvin_to_percentage(self, kelvin: int):
		""" convert kelvin (2700 - 6500) to percentage (0 - 100) """
		return int((kelvin - 2700) / self.color_temp_factor)


	def percentage_to_kelvin(self, percentage: int):
		""" convert percentage (0 - 100) to kelvin (2700 - 6500) """
		return int(self.color_temp_factor * percentage + 2700)
	#endregion color_temp helpers
	#endregion color_temp