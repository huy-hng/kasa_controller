import asyncio
from src.controller import lamp


# bulb = lamp.BulbController('10.0.2.23')
bulb = lamp.BulbController('192.168.178.201')
async def main():
	await bulb.update()
	# await bulb.set_color_temp(0)
	# await bulb.set_brightness(100)
	# await bulb.transition_brightness(100 , 3)
	await bulb.transition_color_temp(0 , 3)
	# await bulb.update()
	# print(bulb.brightness)
	# asyncio.run(bulb.turn_on())

async def test():
	# await bulb.update()
	# await bulb.set_brightness(0)
	await bulb.turn_off(None)
	await asyncio.sleep(1)
	await bulb.turn_on(3000)
	
if __name__ == '__main__':
	# silent_brightnesses = [
	# 	0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
	# ]
	asyncio.run(main())
	# asyncio.run(test())
