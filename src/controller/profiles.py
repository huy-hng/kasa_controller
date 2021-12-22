import time
import datetime
from functools import wraps

import astral
from astral import sun

from src.controller import vlc
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

def bedtime(vlamp=vlc.nom, duration=3600):

	log.info('launching bedtime profile')
	if vlc.active_vlamp.id == 'tom':
		vlc.nom.brightness.value = vlc.active_vlamp.brightness.value
		vlc.tom_to_nom()
	vlamp.brightness.change(0, duration, abort_new=True)


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

def sunset(vlamp=vlc.nom):
	_, duration = get_sunset()

	log.info('running sunset profile')
	
	if vlc.active_vlamp.id == 'tom':
		vlc.nom.color_temp.value = vlc.active_vlamp.color_temp.value
		vlc.tom_to_nom()

	vlamp.color_temp.change(0, duration.seconds, abort_new=True)
		

@helpers.thread
def wake_up(vlamp=vlc.nom, duration=3600):
	log.warning('Running Wake Up profile.')

	if vlc.active_vlamp.id == 'tom':
		vlc.tom_to_nom()
	
	vlamp.brightness.change(1)
	vlamp.color_temp.change(0)
	time.sleep(1)

	vlamp.brightness.change(100, duration/2)
	time.sleep(duration/2)
	vlamp.color_temp.change(100, duration/2)


profiles = {
	'wakeup': wake_up,
	'sunset': sunset,
	'bedtime': bedtime
}
