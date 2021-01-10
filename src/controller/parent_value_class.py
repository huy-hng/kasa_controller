import time
import asyncio
import typing
from dataclasses import dataclass

from src.controller import helpers, bulb
from src.logger import log

# pylint: disable=logging-fstring-interpolation
# pylint: disable=multiple-statements

@dataclass
class Parent:
	_internal_value: int
	_value: int

	internal_valid_range: tuple
	external_valid_range: tuple

	set_val_fn: typing.Callable

	running = False
	should_stop = False
	

	@staticmethod
	def convert_to_internal(external):
		raise NotImplementedError

	@property
	def internal_value(self):
		return self._internal_value
 
	@internal_value.setter
	def internal_value(self, val):
		val = self.check_valid_range(val, self.internal_valid_range)

		self._value = self.convert_to_external(val)
		self._internal_value = val



	@staticmethod
	def convert_to_external(internal):
		raise NotImplementedError

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, val):
		val = self.check_valid_range(val, self.external_valid_range)

		self._value = val
		self._internal_value = self.convert_to_internal(val)






	@staticmethod
	def check_valid_range(val, boundries: tuple):
		if val < boundries[0]: val = boundries[0]
		elif val > boundries[1]: val = boundries[1]
		return val


	@helpers.thread
	def change(self, target_value: int, duration: int=0, start_value: int=None, abort_new=False):
		log.info(f'Changing Value to {target_value}, with duration of {duration}')
		if abort_new and self.running:
			return

		self.wait_for_stop()

		if duration==0 or (duration is None):
			log.debug('Changing immediately since duration is 0')
			self.value = target_value
			self.set_val_fn()
			return


		# asyncio.run(bulb.update())

		if start_value is not None:
			self.value = start_value
			self.set_val_fn()
			time.sleep(1)

		self.running = True
		self.transition(target_value, duration)
		self.running = False


	def transition(self, target_value: int, duration: int):
		raise NotImplementedError


	def wait_for_stop(self):
		if self.running:
			self.should_stop = True

		while self.running:
			time.sleep(0.1)