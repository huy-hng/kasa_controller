import asyncio
from datetime import timedelta

from timeloop import Timeloop

from .controller import bulb, vlc, profiles
from .logger import log
# pylint: disable=logging-fstring-interpolation


tl = Timeloop()

@tl.job(interval=timedelta(seconds=2))
def check_values():
	asyncio.run(bulb.update())
	log.debug('checking if values have changed.')

	if vlc.active_vlamp.brightness.actual != bulb.brightness:
		# if brightness changed
		log.debug(f'brightness manually changed from {vlc.active_vlamp.brightness.actual} to {bulb.brightness}')

		override()
		vlc.active_vlamp.brightness.actual = bulb.brightness


	if vlc.active_vlamp.color_temp.kelvin != bulb.color_temp:
		# if temperature changed
		log.debug(f'temperature manually changed from {vlc.active_vlamp.color_temp.kelvin} to {bulb.color_temp}')

		override()
		vlc.active_vlamp.color_temp.kelvin = bulb.color_temp


	if vlc.active_vlamp.on != bulb.is_on:
		# if lamp turned off/on
		log.debug(f'lamp is on changed to {bulb.is_on}')
		override()
		vlc.active_vlamp.on = bulb.is_on




@tl.job(interval=timedelta(seconds=20))
def check_time():

	profiles.sunset()
	profiles.late()


def override():
	if vlc.active_vlamp.id == 0:
		vlc.override()
