import asyncio
import time

from flask import Flask, request, render_template

import controller
from logger import log

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('home.html')


@app.route('/brightness', methods=['GET', 'POST', 'DELETE'])
def brightness():
  if request.method == 'GET':
    asyncio.run(controller.bulb.update())
    return str(controller.bulb.brightness)
  
  elif request.method == 'POST':
    output = run_task('brightness', request.json)
    return output
  
  elif request.method == 'DELETE':
    controller.stop_bright = True
    return 'Stopped brightness change.'


@app.route('/temp', methods=['GET', 'POST', 'DELETE'])
def color_temp():
  if request.method == 'GET':
    asyncio.run(controller.bulb.update())
    return str(controller.bulb.color_temp)

  elif request.method == 'POST':
    output = run_task('color_temp', request.json)
    return output

  elif request.method == 'DELETE':
    controller.stop_temp = True
    return 'Stopped temperature change.'


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

  fn(target_value, duration, start_value)

  start = ''
  if start_value:
    start = f' from {start_value}'

  return f'Changed {task}{start} to {target_value} in {duration} seconds.'


app.run(debug=True, host='0.0.0.0')
