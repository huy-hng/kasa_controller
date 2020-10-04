import asyncio
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

from src.controller import SINGLE_CHANGE_DUR

executor = ThreadPoolExecutor()

def thread(fn):
	@wraps(fn)
	def wrapper(*args, **kwargs):
		executor.submit(lambda: asyncio.run(fn(*args, **kwargs)))
	return wrapper

def run(fn):
	@wraps(fn)
	def wrapper(*args, **kwargs):
		asyncio.run(fn(*args, **kwargs))
	return wrapper



def calc_steps(diff, amount_of_steps, step_size, curr_val, target):
	step_dir = True if diff > 0 else False

	steps = []
	for _ in range(amount_of_steps):
		curr_val += step_size
		if curr_val > target and step_dir or curr_val < target and not step_dir:
			curr_val = target

		steps.append(curr_val)

	return steps


def calc_sleep_dur(duration, amount_of_steps):
	expected_change_dur = SINGLE_CHANGE_DUR * amount_of_steps
	sleep_dur = duration - expected_change_dur

	if sleep_dur < 0:
		sleep_dur = 0

	single_sleep_dur = sleep_dur / amount_of_steps

	# log.debug(f'sleep_dur={round(sleep_dur, 2)}')
	# log.debug(f'expected_change_dur={round(expected_change_dur, 2)}')
	return single_sleep_dur
