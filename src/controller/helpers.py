import time
import math
import asyncio
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

SINGLE_CHANGE_DUR = 0.12
from src.logger import log

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
