import time
import requests

# location = 'http://10.0.1.102:5000'
location = 'http://localhost:5000'

def get(endpoint, **kwargs):
	requests.get(location+endpoint, params=kwargs)

def debug_vlamp_stuck_in_running():
	reset()
	get('/nom/profile/bedtime')
	time.sleep(15)
	get('/nom/profile/wakeup')

	

def reset():
	get('/nom/set_active')
	get('/nom/brightness', target=100)
	time.sleep(3)


# debug_vlamp_stuck_in_running()
get('/nom/color_temp', target=0)