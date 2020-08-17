import asyncio
import random
import time

async def slow_task(n):
  for _ in range(10):
    await asyncio.sleep(0.1)
    print('from', n)
  print(n, 'done')

async def worker(name, queue):
  print('spawning worker', name)
  while True:
    task = await queue.get()
    await task()
    queue.task_done()
    print(f'{name} is done')


def fn():
  global queue



async def main():
  global queue
  queue = asyncio.Queue()

  # workers = []
  for i in range(6):
    w = asyncio.create_task(worker(f'worker-{i}', queue))
    # workers.append(w)

  queue.put_nowait(lambda: slow_task(0))
  queue.put_nowait(lambda: slow_task(1))
  queue.put_nowait(lambda: slow_task(2))

  while queue.qsize() > 0:
    await queue.join()

queue = None
t0 = time.perf_counter()
asyncio.run(main())
print(round(time.perf_counter() - t0, 2))