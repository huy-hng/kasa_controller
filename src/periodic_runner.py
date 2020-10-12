import asyncio
import time
from datetime import timedelta

from timeloop import Timeloop

from .controller import bulb, vlc, profiles
from .logger import log

tl = Timeloop()

@tl.job(interval=timedelta(seconds=1))
def check_values():
	asyncio.run(bulb.update())

	# TODO: if manual change, switch to override vl

	brightness = vlc.active_vlamp.brightness
	if brightness.actual != bulb.brightness:
		brightness.actual = bulb.brightness

	color_temp = vlc.active_vlamp.color_temp
	if color_temp.kelvin != bulb.color_temp:
		color_temp.kelvin = bulb.color_temp

@tl.job(interval=timedelta(seconds=20))
def check_time():
	now = time.localtime()
	log.debug(f'checking time: {now.tm_hour}:{now.tm_min}')
	
	profiles.sunset()
	profiles.late()