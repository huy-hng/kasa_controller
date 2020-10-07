import time
import datetime
from functools import wraps

import astral
from astral import sun

from src.controller import vlc

location = astral.LocationInfo(timezone='Europe/Berlin', latitude=49.878708, longitude=8.646927)

def run_at(hour: int, minute: int):
  target = datetime.time(hour, minute)

  def actual_decorator(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
      now = time.localtime()
      curr = datetime.time(now.tm_hour, now.tm_min)
      if curr == target:
        function(*args, **kwargs)

    return wrapper
  return actual_decorator


def compare_time(hour: int, minute: int):
	now = time.localtime()
	curr = datetime.time(now.tm_hour, now.tm_min)
	target = datetime.time(hour, minute)
	if curr == target:
		return True
	return False


@run_at(0, 30)
def late():
  vlc.nvl.brightness.change(1, 1800)


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






