import time

from src.controller import helpers
from src.controller.VLamp import VLamp
from src.logger import log

# pylint: disable=logging-fstring-interpolation

class VLampController:
	def __init__(self):
		print('initializing VLampController')
		log.info('initializing VLampController')

		self.nom = VLamp(0, 'Normal Operation Mode')
		self.tom = VLamp(1, 'Temporary Override Mode')
		self.pom = VLamp(2, 'Permanent Override Mode')

		self.vlamps = [self.nom, self.tom, self.pom]

		self.active_vlamp = self.nom
		self.nom.lamp_access = True


	def get_vlamp_by_id(self, id_):
		""" returns vlamp or None if vlamp with given id doesn't exist. """
		for vlamp in self.vlamps:
			if vlamp.id == id_:
				return vlamp


	def transition_lamp_modes(self, target_mode: VLamp, duration):
		self.active_vlamp.brightness.change(target_mode.brightness.perceived, duration)
		self.active_vlamp.color_temp.change(target_mode.color_temp.percent, duration)

	def set_active_lamp(self, id_, duration=1):
		target = self.get_vlamp_by_id(id_)
		if target is None:
			# self.nom.lamp_access = True
			# self.active_vlamp = self.nom
			log.error(f"VLamp with the id of '{id_}' could not been found. Leaving active lamp as is.")
			return

		self.transition_lamp_modes(target, duration)
		while self.active_vlamp.is_running:
			time.sleep(0.1)

		for vlamp in self.vlamps:
			vlamp.lamp_access = False

		target.lamp_access = True
		self.active_vlamp = target

		log.info(f'{self.active_vlamp.name=}')
		log.debug(f'{self.nom.lamp_access=}')
		log.debug(f'{self.tom.lamp_access=}')
		log.debug(f'{self.pom.lamp_access=}')


	def override(self, duration=0, new=True):
		log.info('Overriding nvl')

		if new:
			self.tom = VLamp(1, 'Override VLamp')
			self.tom.brightness.perceived = self.nom.brightness.perceived
			self.tom.color_temp.kelvin = self.nom.color_temp.kelvin

		self.nom.lamp_access = False
		self.tom.lamp_access = True
		self.active_vlamp = self.tom

		if duration > 0:
			self.disengage_in(duration)

	@helpers.thread
	def disengage_in(self, duration):
		time.sleep(duration*60)
		self.disengage()

	def disengage(self, duration=1):
		""" disengages this vlamp and engages the vlamp given as param """
		log.info('Disengaging override, changing lamp access to nvl')

		self.tom.on = self.nom.on
		self.tom.brightness.change(self.nom.brightness.perceived, duration)
		self.tom.color_temp.change(self.nom.color_temp.percent, duration)

		time.sleep(0.5)

		while self.tom.is_running:
			time.sleep(0.1)

		self.nom.lamp_access = True
		self.tom.lamp_access = False
		self.active_vlamp = self.nom

		log.debug('running done')

		
	def is_normal_mode(self):
		return True if self.active_vlamp.id == 0 else False
