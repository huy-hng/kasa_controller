import asyncio
import time
from datetime import timedelta
from timeloop import Timeloop

from .controller import bulb, vlc, profiles

tl = Timeloop()

@tl.job(interval=timedelta(seconds=1))
def check_values():
	asyncio.run(bulb.update())

	brightness = vlc.active_vlamp.brightness
	if brightness.actual != bulb.brightness:
		brightness.actual = bulb.brightness

	color_temp = vlc.active_vlamp.brightness
	if color_temp.kelvin != bulb.color_temp:
		color_temp.kelvin = bulb.color_temp

@tl.job(interval=timedelta(seconds=20))
def check_time():
	sunset_start = profiles.s.sunset_start()
	sunset_duration = profiles.s.sunset_duration()

	if compare_time(sunset_start.hour, sunset_start.minute):
		vlc.nvl.color_temp.change(0, sunset_duration)




