import datetime
from abc import ABC

class Program(ABC):
	priority: int

	turn_off: bool
	brightness: int
	color_temp: int
	first_change: str # if None, both change 

	in_duration: int
	out_duration: int

	start_time: datetime.time
	end_time: datetime.time

