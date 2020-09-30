import math
from dataclasses import dataclass

@dataclass
class Brightness:
	_actual = 0
	_perceived = 0

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
		self._perceived = round(math.sqrt(val*100))

	@perceived.setter
	def perceived(self, val):
		self.check_valid_range(val)
		self._perceived = val
		self._actual = round((val ** 2) / 100) 

	def check_valid_range(val):
		if val < 0 or val > 100:
			raise Exception('Brightness has to be between 0 and 100.')


@dataclass
class ColorTemperature:
	_percent = 0
	_kelvin = 2700

	@property
	def percent(self):
		return self._percent

	@property
	def kelvin(self):
		return self._kelvin

	@percent.setter
	def percent(self, val):
		self._percent = val
		self._kelvin = 38 * val + 2700

	@kelvin.setter
	def kelvin(self, val):
		self._percent = (val - 2700) / 38
		self._kelvin = val

@dataclass
class VLamp:
	SINGLE_CHANGE_DUR = 0.12
	brightness = Brightness()
	color_temp = ColorTemperature()
	# on = True
	
	running_bright = False
	running_temp = False

	stop_bright = False
	stop_temp = False
