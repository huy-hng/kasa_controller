import time

from src.controller import helpers
from src.controller.VLamp import VLamp
from src.logger import log

# pylint: disable=logging-fstring-interpolation

class VLampController:
	def __init__(self):
		log.info('initializing VLampController')

		self.nom = VLamp(id_=0, name='Normal Operation', short_name='nom')
		self.tom = VLamp(id_=1, name='Temporary Override', short_name='tom')
		self.pom = VLamp(id_=2, name='Permanent Override', short_name='pom')
		

		self.all_vlamps = [self.nom, self.tom, self.pom]

		self.active_vlamp = self.nom
		self.nom.lamp_access = True


	def find_vlamp(self, search_term) -> VLamp:
		""" returns vlamp or active_lamp if vlamp with given search_term doesn't exist. """

		try:
			id_ = int(search_term)

		except ValueError:
			log.info(f'Searching for lamp with the short name {search_term}.')
			for vlamp in self.all_vlamps:
				if vlamp.short_name == search_term:
					return vlamp

			log.warning(f'Could not find {search_term}. Returning Active Lamp.')
			return self.active_vlamp

		else:
			log.info(f'Searching for lamp id {id_}.')
			if id_ == -1:
				return self.active_vlamp

			for vlamp in self.all_vlamps:
				if vlamp.id == id_:
					return vlamp



	def set_active_vlamp(self, vlamp: VLamp):
		self.active_vlamp = vlamp
		for vlamp in self.all_vlamps:
			vlamp.lamp_access = False
		vlamp.lamp_access = True



	def transition_to_vlamp(self, target_vlamp: VLamp, transition_duration=0):
		temporary_vlamp = VLamp(99, 'Temporary Vlamp', 'temp')
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