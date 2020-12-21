import time
from functools import wraps

from ..controller import helpers
from ..logger import log
# pylint: disable=logging-fstring-interpolation

def looper(sleep: int):
	def decorator(function):
		def runner():
			log.debug('running loop')
			while True:
				function()
				time.sleep(sleep)

		@wraps(function)
		def wrapper():
			log.debug('running executor')
			future = helpers.executor.submit(runner)
			helpers.executor.submit(helpers.check_for_error, future, function.__name__)
		return wrapper
	return decorator