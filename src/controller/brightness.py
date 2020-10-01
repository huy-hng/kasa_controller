import math
import asyncio

from src.controller import bulb, helpers, vl
from src.logger import log

@helpers.runner
async def change_brightness(target_value: int, duration: int, start_value: int=None):
	vl.running_bright = True
	await bulb.turn_on()
	await bulb.update()

	log.warning('')
	log.info(f'{start_value=} curr_value={bulb.brightness} {target_value=} {duration=}')

	if duration==0:
		# change immediately
		await set_brightness(target_value)
		vl.running_bright = False
		return
	elif start_value is not None:
		# use bulb.set_brightness bc set_brightness has a turn off feature
		vl.brightness.perceived = start_value
		await bulb.set_brightness(vl.brightness.actual)
		
	await transition_bright(target_value, duration)
	vl.running_bright = False


async def set_brightness(value):
	turn_off = False
	if value == 0:
		value = 1
		turn_off = True

	vl.brightness.perceived = value
	log.debug(f'brightness={vl.brightness}')
	await bulb.set_brightness(vl.brightness.actual)

	if turn_off:
		log.info(f'Brightness was set to 0, turning lamp off.')
		await asyncio.sleep(0.2)
		await bulb.turn_off()


async def transition_bright(target_value: int, duration: int):
	curr_value = vl.brightness.perceived # TODO: check if this line introduces bugs

	diff, cond = helpers.get_diff(curr_value, target_value)
	if diff == 0:
		if curr_value == 0:
			await bulb.turn_off()
			log.info(f'turning off')
		else:
			log.info(f'exiting, no difference')
		return # return when theres no change to make

	amount_of_steps, step_size = get_steps(duration, diff)
	single_sleep_dur = helpers.calc_sleep_dur(duration, amount_of_steps)

	log.info(f'{curr_value=} {target_value=} {amount_of_steps=} {single_sleep_dur=}')
	
	await helpers.transition(curr_value, target_value, cond, set_brightness, step_size, single_sleep_dur)


def get_steps(duration, diff):
	step_size = (diff * vl.SINGLE_CHANGE_DUR) / (duration)
	
	if abs(step_size) < 2:
		step_size = 2 if step_size > 0 else -2
	elif step_size < 0:
		step_size = math.floor(step_size)
	else:
		step_size = math.ceil(step_size)

	# log.debug(f'{step_size=}')
	amount_of_steps = math.ceil(diff / step_size)
	return amount_of_steps, step_size
