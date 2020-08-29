import time
import math
import asyncio
from functools import wraps
from concurrent.futures import ThreadPoolExecutor


from kasa import SmartBulb

from logger import log

SINGLE_CHANGE_DUR = 0.12

bulb = SmartBulb('10.0.2.23')


##################
#region Variables#
##################

stop_bright = False
stop_temp = False

#endregion
##################

################
#region Helpers#
################
executor = ThreadPoolExecutor()

def runner(fn):
	@wraps(fn)
	def wrapper(*args, **kwargs):
		executor.submit(lambda: asyncio.run(fn(*args, **kwargs)))
	return wrapper

def perceived2actual_brightness(perceived):
	return round((perceived ** 2) / 100)

def actual2perceived_brightness(actual_brightness):
	return round(math.sqrt(actual_brightness*100))

def round_to_nearest_100(x, base=100):
	return int(base * round(float(x)/base))

def get_diff(curr_val, target_val):
	diff = target_val - curr_val
	if diff > 0:
		cond = lambda curr_val: curr_val < target_val
	else:
		cond = lambda curr_val: curr_val > target_val

	# log.debug(f'{diff=}')
	return diff, cond

def calc_sleep_dur(duration, amount_of_steps):
	expected_change_dur = SINGLE_CHANGE_DUR * amount_of_steps
	sleep_dur = duration - expected_change_dur

	if sleep_dur < 0:
		sleep_dur = 0

	single_sleep_dur = sleep_dur / amount_of_steps

	# log.debug(f'sleep_dur={round(sleep_dur, 2)}')
	# log.debug(f'expected_change_dur={round(expected_change_dur, 2)}')
	return single_sleep_dur

async def transition(curr_value, target_value, cond, fn, step_size, single_sleep_dur):
	global stop_bright
	global stop_temp
	t0 = time.perf_counter()
	while cond(curr_value):
		curr_value += step_size

		if not cond(curr_value):
			# check that curr_value doesnt overshoot target_value
			curr_value = target_value

		if fn.__name__ == 'set_brightness' and stop_bright or \
				fn.__name__ == 'set_color_temp' and stop_temp:
			stop_temp = False
			stop_bright = False
			break

		await fn(curr_value)

		await asyncio.sleep(single_sleep_dur)
		# time.sleep(single_sleep_dur)

	t1 = time.perf_counter() - t0
	# log.debug(f'actual_change_dur={round(t1-sleep_dur, 4)}')
	log.info(f'actual_complete_dur={round(t1, 4)}')
#endregion Helpers
################



###################
#region Brightness#
###################
@runner
async def change_brightness(target_value: int, duration: int, start_value: int=None):
	await bulb.turn_on()
	await bulb.update()

	log.warning('')
	log.info(f'{start_value=} curr_value={bulb.brightness} {target_value=} {duration=}')

	if duration==0:
		await set_brightness(target_value)
		return
	elif start_value is not None:
		# use bulb.set_brightness bc set_brightness has a turn off feature
		await bulb.set_brightness(perceived2actual_brightness(start_value))
		
	await transition_bright(target_value, duration)


async def set_brightness(value):
	turn_off = False
	if value == 0:
		value = 1
		turn_off = True

	actual_brightness = perceived2actual_brightness(value)
	log.debug(f'perceived_brightness={value}|{actual_brightness=}')
	await bulb.set_brightness(actual_brightness)

	if turn_off:
		log.info(f'brightness is 0, turning lamp off')
		await asyncio.sleep(0.2)
		await bulb.turn_off()


async def transition_bright(target_value: int, duration: int):
	curr_value = actual2perceived_brightness(bulb.brightness)

	diff, cond = get_diff(curr_value, target_value)
	if diff == 0:
		if curr_value == 0:
			await bulb.turn_off()
			log.info(f'turning off')
		else:
			log.info(f'exiting, no difference')
		return # return when theres no change to make

	amount_of_steps, step_size = get_steps(duration, diff)
	single_sleep_dur = calc_sleep_dur(duration, amount_of_steps)

	log.info(f'{curr_value=} {target_value=} {amount_of_steps=} {single_sleep_dur=}')
	
	await transition(curr_value, target_value, cond, set_brightness, step_size, single_sleep_dur)


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

#endregion
###################



####################
#region Temperature#
####################
@runner
async def change_temperature(target_value: int, duration: int, start_value: int=None):
	await bulb.turn_on()
	await bulb.update()

	log.warning('')

	if duration==0:
		await set_color_temp(target_value)
		return
	elif start_value is not None:
		await set_color_temp(start_value)
		
	await transition_color_temp(target_value, duration)


async def set_color_temp(value):
	log.debug(f'change temp to {value}')
	await bulb.set_color_temp(value)


async def transition_color_temp(target_t: int, duration:int):
	target_value = 38 * target_t + 2700
	curr_value = bulb.color_temp

	diff, cond = get_diff(curr_value, target_value)
	if diff == 0:
		return # return when theres no change to make

	#region calc step_size
	step_size = (diff * SINGLE_CHANGE_DUR) / duration

	if abs(step_size) < 100:
		step_size = 100 if step_size > 0 else -100

	step_size = round_to_nearest_100(step_size)
	log.info(f'{step_size=}')
	#endregion

	amount_of_steps = math.ceil(diff / step_size)
	single_sleep_dur = calc_sleep_dur(duration, amount_of_steps)

	log.info(f'{curr_value=} {target_value=} {amount_of_steps=} {single_sleep_dur=}')

	await transition(curr_value, target_value, cond, set_color_temp, step_size, single_sleep_dur)
#endregion Temperature
####################


if __name__ == '__main__':
	asyncio.run(bulb.update())

	b = 50 if bulb.brightness == 100 else 100
	c = 0 if bulb.color_temp == 6500 else 100

	change_brightness(b, 2)
	change_temperature(c, 2)
	