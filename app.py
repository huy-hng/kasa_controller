import asyncio
import time
import threading

from flask import Flask, request, render_template

import controller
from logger import log

app = Flask(__name__)
loop = asyncio.new_event_loop()

@app.route('/')
def home():
  return render_template('home.html')


@app.route('/brightness', methods=['GET', 'POST'])
def brightness():
  if request.method == 'GET':
    asyncio.run(controller.bulb.update())
    return str(controller.bulb.brightness)

  t0 = time.perf_counter()
  output = run_task('brightness', request.json)
  log.info(round(time.perf_counter() - t0, 2))
  return output


@app.route('/temp', methods=['GET', 'POST'])
def color_temp():
  if request.method == 'GET':
    asyncio.run(controller.bulb.update())
    return str(controller.bulb.color_temp)

  output = run_task('color_temp', request.json)
  return output


@app.route('/state', methods=['GET', 'POST'])
def state():
  if request.method == 'GET':
    asyncio.run(controller.bulb.update())
    return 'on' if controller.bulb.is_on else 'off'

  data = request.json
  if data['state']:
    asyncio.run(controller.bulb.turn_on())
  else:
    asyncio.run(controller.bulb.turn_off())

  return 'done'

def run_task(task, data):
  target_value = data['target']
  duration = data['duration']
  start_value = data.get('start_value')

  fn = None
  if task == 'brightness':
    fn = controller.change_brightness
  elif task == 'color_temp':
    fn = controller.change_temperature

  # log.info(loop.is_running())
  # asyncio.create_task(fn(target_value, duration, start_value))
  queue.put_nowait((fn, {
    'target_value': target_value,
    'duration': duration,
    'start_value': start_value
  }))

  start = ''
  if start_value:
    start = f' from {start_value}'

  return f'Changed {task}{start} to {target_value} in {duration} seconds.'


async def worker(name, queue):
  log.info(f'spawning worker {name}')
  while True:
    task, kwargs = await queue.get()
    log.info(f'{task}, {kwargs}')
    await task(kwargs)
    queue.task_done()

    log.info(f'{name} is done')


async def main():
  global queue
  queue = asyncio.Queue()
  for i in range(3):
    asyncio.create_task(worker(f'worker-{i}', queue))

  threading.Thread(target=app.run).start()

  # app.run(debug=True, host='0.0.0.0')


  # await queue.join()
# if __name__ == '__main__':
  # executor.submit(loop.run_forever)
  # app.run(debug=True, host='0.0.0.0')

queue = None
asyncio.run(main())