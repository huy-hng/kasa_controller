import math
import asyncio

from src.controller import bulb, helpers, vl
from src.controller.state import ColorTemperature
from src.logger import log

@helpers.runner
async def change_temperature(target_value: int, duration: int, start_value: int=None):
	vl.running_temp = True
	await bulb.turn_on()
	await bulb.update()

	log.warning('')

	if duration==0:
		await set_color_temp(target_value)
		vl.running_temp = False
		return
	elif start_value is not None:
		await set_color_temp(start_value)
		
	await transition_color_temp(target_value, duration)
	vl.running_temp = False


async def set_color_temp(value):
	log.debug(f'change temp to {value}')
	vl.color_temp = value
	await bulb.set_color_temp(vl.color_temp)


async def transition_color_temp(target_t: int, duration:int):
	temp = ColorTemperature()
	temp.percent = target_t
	curr_value = bulb.color_temp

	diff, cond = helpers.get_diff(curr_value, temp.kelvin)
	if diff == 0:
		return # return when theres no change to make

	#region calc step_size
	step_size = (diff * vl.SINGLE_CHANGE_DUR) / duration

	if abs(step_size) < 100:
		step_size = 100 if step_size > 0 else -100

	step_size = helpers.round_to_nearest_100(step_size)
	log.info(f'{step_size=}')
	#endregion

	amount_of_steps = math.ceil(diff / step_size)
	single_sleep_dur = helpers.calc_sleep_dur(duration, amount_of_steps)

	log.info(f'{curr_value=} {temp.kelvin=} {amount_of_steps=} {single_sleep_dur=}')

	await helpers.transition(curr_value, temp.kelvin, cond, set_color_temp, step_size, single_sleep_dur)
