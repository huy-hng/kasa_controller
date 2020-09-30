import math
from dataclasses import dataclass

@dataclass
class Brightness:
	_actual: int = 0
	_perceived: int = 0


	@property
	def actual(self):
		return self._actual

	@property
	def perceived(self):
		return self._perceived

	@actual.setter
	def actual(self, val):
		self.check_valid_range(val)
		self._actual = val
		self._perceived = self.actual2perceived_brightness(val)

	@perceived.setter
	def perceived(self, val):
		self.check_valid_range(val)
		self._perceived = val
		self._actual = self.perceived2actual_brightness(val)

	def check_valid_range(val):
		if val < 0 or val > 100:
			raise Exception('Brightness has to be between 0 and 100.')

	@staticmethod
	def perceived2actual_brightness(perceived) -> int:
		return round((perceived ** 2) / 100) 

	@staticmethod
	def actual2perceived_brightness(actual_brightness) -> int:
		return round(math.sqrt(actual_brightness*100))


@dataclass
class VLamp:
	brightness = Brightness()
	color_temp = 2700
	# on = True
	
	running_bright = False
	running_temp = False

	stop_bright = False
	stop_temp = False
