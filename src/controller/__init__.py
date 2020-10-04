import asyncio

from kasa import SmartBulb

bulb = SmartBulb('10.0.2.23')
asyncio.run(bulb.update())
SINGLE_CHANGE_DUR = 0.12

from src.controller.VLampController import VLampController
vlc = VLampController()
