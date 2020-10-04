import datetime
from dataclasses import dataclass

import astral
from astral import sun

location = astral.LocationInfo(timezone='Europe/Berlin', latitude=49.878708, longitude=8.646927)

print(location.timezone)

s = sun.sun(location.observer,
        date=datetime.datetime.now(),
        tzinfo=location.timezone)


for k, v in s.items():
  print(k, v)
# def sunset():

@dataclass
class Sun:
  observer = location.observer
  date = lambda x: datetime.datetime.now()
  tzinfo = location.timezone

  def golden_hour(self):
    return sun.twilight(self.observer, date=self.date(), direction='SETTING', tzinfo=self.tzinfo)


s = Sun()
for d in s.golden_hour():
  print(d)