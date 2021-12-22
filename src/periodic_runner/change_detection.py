import asyncio

from src.controller import bulb, vlc
from src.logger import log
# pylint: disable=logging-fstring-interpolation

def has_brightness_changed():
	return vlc.active_vlamp.brightness.internal_value != bulb.brightness

def has_color_temp_changed():
	return vlc.active_vlamp.color_temp.internal_value != bulb.color_temp

def has_on_state_changed():
	return vlc.active_vlamp.on != bulb.is_on




def check_changes():
	asyncio.run(bulb.update())
	log.debug('Checking values')
	
	if vlc.active_vlamp.is_running:
		log.debug('vlamp is running, skipping check')
		return

	if has_on_state_changed():
		log.debug(f'lamp is on changed to {bulb.is_on}')
		vlc.active_vlamp.sync()

	# if has_brightness_changed():
	# 	log.debug(f'brightness manually changed from {vlc.active_vlamp.brightness.actual} to {bulb.brightness}')
	# 	vlc.active_vlamp.sync()

	# if has_color_temp_changed():
	# 	log.debug(f'temperature manually changed from {vlc.active_vlamp.color_temp.kelvin} to {bulb.color_temp}')
	# 	vlc.active_vlamp.sync()
