import asyncio
import time

async def test():
    print(asyncio.get_running_loop())
    time.sleep(1)
    print('done')



asyncio.run(test())