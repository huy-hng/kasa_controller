import time
import math
import asyncio
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

from src import controller
from src.logger import log

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
	expected_change_dur = controller.SINGLE_CHANGE_DUR * amount_of_steps
	sleep_dur = duration - expected_change_dur

	if sleep_dur < 0:
		sleep_dur = 0

	single_sleep_dur = sleep_dur / amount_of_steps

	# log.debug(f'sleep_dur={round(sleep_dur, 2)}')
	# log.debug(f'expected_change_dur={round(expected_change_dur, 2)}')
	return single_sleep_dur

async def transition(curr_value, target_value, cond, fn, step_size, single_sleep_dur):
	t0 = time.perf_counter()
	while cond(curr_value):
		curr_value += step_size

		if not cond(curr_value):
			# check that curr_value doesnt overshoot target_value
			curr_value = target_value

		if fn.__name__ == 'set_brightness' and controller.stop_bright or \
				fn.__name__ == 'set_color_temp' and controller.stop_temp:
			controller.stop_temp = False
			controller.stop_bright = False
			break

		await fn(curr_value)

		await asyncio.sleep(single_sleep_dur)
		# time.sleep(single_sleep_dur)

	t1 = time.perf_counter() - t0
	# log.debug(f'actual_change_dur={round(t1-sleep_dur, 4)}')
	log.info(f'actual_complete_dur={round(t1, 4)}')
