import asyncio
import random
import time

async def slow_task():
  await asyncio.sleep(0.5)
  print('task done')

async def worker(name, queue):
  print('spawning worker', name)
  while True:
    task = await queue.get()
    await task()
    queue.task_done()
    print(f'{name} is done')


def fn():
  global queue
  for _ in range(6):
    queue.put_nowait(slow_task)


async def main():
  global queue
  queue = asyncio.Queue()

  # workers = []
  for i in range(6):
    w = asyncio.create_task(worker(f'worker-{i}', queue))
    # workers.append(w)



  while queue.qsize() > 0:
    await queue.join()

queue = None
t0 = time.perf_counter()
asyncio.run(main())
print(round(time.perf_counter() - t0, 2))