import asyncio

from ..controller import bulb, vlc
from ..logger import log
# pylint: disable=logging-fstring-interpolation

def override():
	if vlc.active_vlamp.id == 0:
		vlc.override(0, False)



def check_changes():
	asyncio.run(bulb.update())
	log.debug('Checking values')
	
	if vlc.active_vlamp.is_running:
		log.debug('vlamp is running, skipping check')
		return

	if vlc.active_vlamp.brightness.internal_value != bulb.brightness:
		# if brightness changed
		log.debug(f'brightness manually changed from {vlc.active_vlamp.brightness.actual} to {bulb.brightness}')

		override()
		vlc.active_vlamp.brightness.internal_value = bulb.brightness


	if vlc.active_vlamp.color_temp.internal_value != bulb.color_temp:
		# if temperature changed
		log.debug(f'{vlc.active_vlamp.name}')
		log.debug(f'temperature manually changed from {vlc.active_vlamp.color_temp.kelvin} to {bulb.color_temp}')

		override()
		vlc.active_vlamp.color_temp.internal_value = bulb.color_temp


	if vlc.active_vlamp.on != bulb.is_on:
		# if lamp turned off/on
		log.debug(f'lamp is on changed to {bulb.is_on}')
		override()
		vlc.active_vlamp.on = bulb.is_on
