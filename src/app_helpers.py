from functools import wraps

from flask import jsonify
from src.controller import vlc

def vlamp_required(function):
	@wraps(function)
	def wrapper(vlamp, *args, **kwargs):

		try:
			vlamp = vlc.find_vlamp(vlamp)
		except:
			return jsonify(success=False, 
										message=f'VLamp {vlamp} does not exist.'), 400
		else:
			return function(vlamp, *args, **kwargs)
			
	return wrapper