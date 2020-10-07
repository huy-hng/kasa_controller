import datetime
from dataclasses import dataclass

import astral
from astral import sun

location = astral.LocationInfo(timezone='Europe/Berlin', latitude=49.878708, longitude=8.646927)

print(astral.now(tzinfo=location.timezone))

s = sun.sun(location.observer,
        date=datetime.datetime.now(),
        tzinfo=location.timezone)


# for k, v in s.items():
#   print(k, v)

def sunset():
	start = sun.golden_hour(
    location.observer,
    date=datetime.datetime.now(),
    direction=astral.SunDirection.SETTING,
    tzinfo=location.timezone
  )[0]

	duration = sun.dusk(
    location.observer,
    date=datetime.datetime.now(),
    tzinfo=location.timezone
  )

	if compare_time(start.hour, start.minute):
		vlc.nvl.color_temp.change(0, duration)


def compare_time(hour, minute):
	now = time.localtime()
	curr = datetime.time(now.tm_hour, now.tm_min)
	target = datetime.time(hour, minute)
	if curr == target:
		return True
	return False
