import datetime

import astral
from astral import sun

from src.programs.abstract_program import Program

class Sun(Program):
	priority = 1

	location = astral.LocationInfo(timezone='Europe/Berlin',
																 latitude=49.878708,
																 longitude=8.646927)

	@property
	def in_duration(self):
		return self.end_sunset_time - self.start_time

	@property
	def out_duration(self):
		return self.end_sunrise_time - self.end_time

	# async def start(self):
	# 	""" Changes Color Temp to warm """
	# 	_, duration = self.get_sunset()
	# 	self.bulb.transition_color_temp(0, duration.seconds)


	@property
	def start_time(self):
		""" start sunset time """
		start_sunset = sun.golden_hour(
			self.location.observer,
			date=datetime.datetime.now(),
			direction=astral.SunDirection.SETTING,
			tzinfo=self.location.timezone
		)[0] # index 0 is start time

		# start_sunset = convert_datetime_to_time(start_sunset)
		return start_sunset


	def end_sunset_time(self):
		return sun.dusk(
			self.location.observer,
			date=datetime.datetime.now(),
			tzinfo=self.location.timezone
		)

	@property
	def end_time(self):
		""" start sunrise time """
		start_sunrise = sun.golden_hour(
			self.location.observer,
			date=datetime.datetime.now(),
			direction=astral.SunDirection.RISING,
			tzinfo=self.location.timezone
		)[0]
		return start_sunrise


	def end_sunrise_time(self):
		return sun.dawn(
			self.location.observer,
			date=datetime.datetime.now(),
			tzinfo=self.location.timezone
		)

if __name__ == '__main__':
	sun_ = Sun()
	sun_.start_time