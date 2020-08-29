import asyncio
from src.controller.brightness import change_brightness
from src.controller.temperature import change_temperature
from src.controller import bulb


asyncio.run(bulb.update())

b = 50 if bulb.brightness == 100 else 100
c = 0 if bulb.color_temp == 6500 else 100

print(b)
change_brightness(b, 1)
change_temperature(c, 1)
