import asyncio
import random
import time

from functools import wraps
from concurrent.futures import ThreadPoolExecutor


executor = ThreadPoolExecutor()

def runner(fn):
  @wraps(fn)
  def wrapper(*args, **kwargs):
    executor.submit(lambda: asyncio.run(fn(*args, **kwargs)))
  return wrapper

@runner
async def slow_task(n):
  for _ in range(10):
    await asyncio.sleep(0.1)
    print('from', n)
  print(n, 'done')


def main():

    slow_task(0)
    slow_task(1)

main()
