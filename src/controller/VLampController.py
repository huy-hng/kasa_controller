import time

from src import exceptions
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
				log.info(f'Found VLamp with id {vlamp.id}')
				return vlamp

		not_found_message = f'Could not find VLamp {id_}.'
		log.warning(not_found_message)
		raise exceptions.VLampNotFoundException(not_found_message)


	def set_active_vlamp(self, vlamp: VLamp):
		self.active_vlamp = vlamp
		
		for v in self.all_vlamps:
			v.lamp_access = False

		vlamp.lamp_access = True


	def transition_to_vlamp(self, target_vlamp: VLamp, transition_duration=0):
		log.info(f'Transitioning to VLamp {target_vlamp.name} with duration of {transition_duration}')
		log.debug(f'{transition_duration}, {type(transition_duration)}')

		temporary_vlamp = VLamp('temp', 'Temporary Vlamp')
		self.all_vlamps.append(temporary_vlamp)

		self.copy_vlamp(temporary_vlamp)


		temporary_vlamp.brightness.change(target_vlamp.brightness.value, transition_duration)
		temporary_vlamp.color_temp.change(target_vlamp.color_temp.value, transition_duration)
		
		while temporary_vlamp.is_running:
			time.sleep(0.1)
			
		log.debug(f'Transition done.')

		self.all_vlamps.remove(temporary_vlamp)

		self.set_active_vlamp(target_vlamp)

	def copy_vlamp(self, target_vlamp: VLamp):
		target_vlamp.brightness.value = self.active_vlamp.brightness.value
		target_vlamp.color_temp.value = self.active_vlamp.color_temp.value

		self.set_active_vlamp(target_vlamp)


	def change_to_nom(self):
		if self.active_vlamp == 'tom':
			vlamp = self.find_vlamp('nom')
			self.transition_to_vlamp(vlamp, 1)


	def state(self):
		state = {vlamp.id: vlamp.state for vlamp in self.all_vlamps}
		state.update({
			'active_vlamp_name': self.active_vlamp.name,
			'active_vlamp_id': self.active_vlamp.id,
		})
		return state