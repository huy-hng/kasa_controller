import asyncio
from kasa import SmartBulb

bulb = SmartBulb('10.0.2.23')

async def main():
	await bulb.update()
	try:
		await bulb.set_brightness(101)
	except ValueError as e:
		print('Invalid brightness' in str(e))

asyncio.run(main())