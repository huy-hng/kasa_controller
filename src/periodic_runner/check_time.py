import time
import datetime

from src.periodic_runner import looper
from src.controller import profiles
from src.logger import log
# pylint: disable=logging-fstring-interpolation


def compare_time(hour: int, minute: int):
	now = time.localtime()
	curr = datetime.time(now.tm_hour, now.tm_min)
	target = datetime.time(hour, minute)
	if curr == target:
		return True
	return False


@looper(20)
def check_time():
	sunset_start, _ = profiles.get_sunset()
	if compare_time(sunset_start.hour, sunset_start.minute):
		profiles.sunset()
		
	# if compare_time(0, 30):
	# 	profiles.bedtime()
