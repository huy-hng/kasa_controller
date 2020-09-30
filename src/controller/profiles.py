import datetime

import astral
from astral.sun import sun

location = astral.LocationInfo(timezone='Europe/Berlin', latitude=49.878708, longitude=8.646927)

print(location.timezone)

s = sun(location.observer,
        date=datetime.datetime.now(),
        tzinfo=location.timezone)


for k, v in s.items():
  print(k, v)
# def sunset():
