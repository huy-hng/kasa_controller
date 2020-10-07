import time

now = time.localtime()
# print(now)
now = {
	'hour': now.tm_hour,
	'min': now.tm_min
}


import datetime

def compare_time(hour, minute):
	now = time.localtime()
	curr = datetime.time(now.tm_hour, now.tm_min)
	target = datetime.time(hour, minute)
	if curr == target:
		return True
	return False

equal = compare_time(18, 4)
print(equal)
