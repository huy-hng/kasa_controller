import time
import datetime
from functools import wraps

import astral
from astral import sun

from src.controller import vlc, bulb
from . import helpers
from src.logger import log

location = astral.LocationInfo(timezone='Europe/Berlin', latitude=49.878708, longitude=8.646927)

def run_at(hour: int, minute: int):
	target = datetime.time(hour, minute)

	def actual_decorator(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
			now = time.localtime()
			curr = datetime.time(now.tm_hour, now.tm_min)
			if curr == target:
				function(*args, **kwargs)

		return wrapper
	return actual_decorator

def late(vlamp=vlc.nvl):
	log.info('launching late profile')
	vlamp.brightness.change(1, 1800, abort_new=True)


def get_sunset():
	start = sun.golden_hour(
		location.observer,
		date=datetime.datetime.now(),
		direction=astral.SunDirection.SETTING,
		tzinfo=location.timezone
	)[0]

	end = sun.dusk(
		location.observer,
		date=datetime.datetime.now(),
		tzinfo=location.timezone
	)

	duration = end - start

	return start, duration

def sunset(vlamp=vlc.nvl):
	_, duration = get_sunset()

	log.info('running sunset profile')
	vlamp.color_temp.change(0, duration.seconds, abort_new=True)
		

@helpers.thread
@helpers.run
async def wake_up(vlamp=vlc.nvl):
	log.warning('Running Wake Up profile.')
	await bulb.turn_on()
	await bulb.update()
	duration = 600
	vlamp.brightness.change(100, duration/2)
	time.sleep(duration/2)
	vlamp.color_temp.change(100, duration/2)


profiles = {
	'wakeup': wake_up,
	'sunset': sunset,
	'late': late
}