import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, render_template

import controller
from logger import log

app = Flask(__name__)

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

  executor.submit(lambda: asyncio.run(fn(target_value, duration, start_value)))
  # fn(target_value, duration, start_value)


  

  start = ''
  if start_value:
    start = f' from {start_value}'

  return f'Changed {task}{start} to {target_value} in {duration} seconds.'


executor = ThreadPoolExecutor()
app.run(debug=True, host='0.0.0.0')
