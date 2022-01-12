from src.programs.abstract_program import Program

class Sleep(Program):
	priority = 2

	turn_off = True
	brightness = 0
	color_temp = 0

	in_duration = 3600
	out_duration = 3600

	""" 
		# async def start(self, duration: int=3600):

		# 	await self.bulb.transition_color_temp(0, duration/2)
		# 	await self.bulb.turn_off(duration/2)

		# async def end(self, duration: int=3600):
		# 			Prerequisites: lamp has been turned off
		# 			with BulbController.turn_off()
		# 	await self.bulb.transition_brightness(100, duration/2)
	"""


