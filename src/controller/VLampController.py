from src.controller.VLamp import VLamp
from src.logger import log

class VLampController:
	def __init__(self):
		self.nvl = VLamp('normal')
		self.nvl.lamp_access = True

		self.active_vlamp = self.nvl
		self.ovl = self.nvl.override()
		
	def is_normal_mode(self):
		return True if self.active_vlamp.name == 'normal' else False

	def new_override(self):
		log.info(f'new override')
		self.ovl = self.active_vlamp.override()
		self.active_vlamp = self.ovl
	
	def disengage(self, duration=1):
		log.info(f'disengaging, returning to nvl')
		self.ovl.disengage(self.nvl, duration)
		self.active_vlamp = self.nvl
