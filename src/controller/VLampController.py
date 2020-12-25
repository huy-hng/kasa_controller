import time

from src.controller import helpers
from src.controller.VLamp import VLamp
from src.logger import log

# pylint: disable=logging-fstring-interpolation

class VLampController:
	def __init__(self):
		log.info('initializing VLampController')

		self.nom = VLamp(0, 'Normal Operation')
		self.tom = VLamp(1, 'Temporary Override')
		self.pom = VLamp(2, 'Permanent Override')

		self.vlamps = [self.nom, self.tom, self.pom]

		self.active_vlamp = self.nom
		self.nom.lamp_access = True


	def get_vlamp_by_id(self, id_) -> VLamp:
		""" returns vlamp or None if vlamp with given id doesn't exist. """
		try:
			id_ = int(id_)
		except ValueError:
			log.error(f'{id_} is not a valid id.')
			return self.active_vlamp

		if id_ == -1:
			return self.active_vlamp

		for vlamp in self.vlamps:
			if vlamp.id == id_:
				return vlamp

		return None


	def transition_lamp_modes(self, target_mode: VLamp, duration):
		self.active_vlamp.brightness.change(target_mode.brightness.value, duration)
		self.active_vlamp.color_temp.change(target_mode.color_temp.value, duration)
		while self.active_vlamp.is_running:
			time.sleep(0.1)


	def set_active_vlamp(self, id_, duration=1):
		target = self.get_vlamp_by_id(id_)

		if target is None:
			log.error(f"VLamp with the id of '{id_}' could not been found. Leaving active lamp as is.")
			return

		self.transition_lamp_modes(target, duration)

		for vlamp in self.vlamps:
			vlamp.lamp_access = False

		target.lamp_access = True
		self.active_vlamp = target

		log.info(f'{self.active_vlamp.name=}')
		log.debug(f'{self.nom.lamp_access=}')
		log.debug(f'{self.tom.lamp_access=}')
		log.debug(f'{self.pom.lamp_access=}')
