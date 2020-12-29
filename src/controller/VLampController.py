import time

from src import exceptions
from src.controller import helpers
from src.controller.VLamp import VLamp
from src.logger import log

# pylint: disable=logging-fstring-interpolation

class VLampController:
	def __init__(self):
		log.info('initializing VLampController')

		self.nom = VLamp(id_='nom', name='Normal Operation')
		self.tom = VLamp(id_='tom', name='Temporary Override')
		self.pom = VLamp(id_='pom', name='Permanent Override')
		

		self.all_vlamps = [self.nom, self.tom, self.pom]

		self.active_vlamp = self.nom
		self.nom.lamp_access = True


	def find_vlamp(self, id_: str) -> VLamp:
		""" returns vlamp or active_lamp if vlamp with given id doesn't exist. """

		log.info(f'Searching for lamp with id {id_}.')
		for vlamp in self.all_vlamps:
			if vlamp.id == id_:
				return vlamp

		not_found_message = f'Could not find VLamp {id_}.'
		log.warning(not_found_message)
		raise exceptions.VLampNotFoundException(not_found_message) # TODO: test this



	def set_active_vlamp(self, vlamp: VLamp):
		self.active_vlamp = vlamp
		for vlamp in self.all_vlamps:
			vlamp.lamp_access = False
		vlamp.lamp_access = True



	def transition_to_vlamp(self, target_vlamp: VLamp, transition_duration=0):
		temporary_vlamp = VLamp('temp', 'Temporary Vlamp')
		self.all_vlamps.append(temporary_vlamp)

		self.set_active_vlamp(temporary_vlamp)

		temporary_vlamp.brightness.change(target_vlamp.brightness.value, transition_duration)
		temporary_vlamp.color_temp.change(target_vlamp.color_temp.value, transition_duration)
		
		while temporary_vlamp.is_running:
			time.sleep(0.1)

		self.all_vlamps.remove(temporary_vlamp)

		self.set_active_vlamp(target_vlamp)


	def state(self):
		pass