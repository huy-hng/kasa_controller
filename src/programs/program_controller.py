import time
import datetime

from src.programs.abstract_program import Program

class ProgramController:
	programs: dict[str, Program] = {}
	active_programs: list[Program] = []

	def register_program(self, program: Program):
		self.programs.append(program)

	def activate_program(self, program: Program):
		"""
			add program to active program list
			transition to program (via program.start())

			edge cases:
				- program is already in list
				- same priority is already in list
		"""	


	def deactivate_program(self, program):
		pass
		# pop program from active list
		#	transition to layer below

	def check_for_program_start(self):
		current_time = None # TODO
		now = time.localtime()
		current_time = datetime.time(now.tm_hour, now.tm_min)
		for name, program in self.programs.items():
			try:
				if program.start_time == current_time:
					self.activate_program(program)
			except AttributeError:
				pass