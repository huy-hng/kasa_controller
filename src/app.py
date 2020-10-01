import asyncio
import time

from flask import Flask, request, render_template

from . import controller
from .controller import vl
from .logger import log

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('home.html', vlamp=vl)


@app.route('/brightness', methods=['GET', 'POST', 'DELETE'])
def brightness():
  if request.method == 'GET':
    asyncio.run(controller.bulb.update())
    return (
      f'perceived_brightness={str(vl.brightness.perceived)}\n'
      f'actual_brightness={str(vl.brightness.actual)}\n'
      f'running={vl.running_bright}'
    )
  
  elif request.method == 'POST':
    output = run_task('brightness', request.json)
    return output
  
  elif request.method == 'DELETE':
    vl.stop_bright = True
    return 'Stopped brightness change.'


@app.route('/temp', methods=['GET', 'POST', 'DELETE'])
def color_temp():
  if request.method == 'GET':
    asyncio.run(controller.bulb.update())
    return f'temperature={str(vl.color_temp)}\nrunning={vl.running_temp}'

  elif request.method == 'POST':
    output = run_task('color_temp', request.json)
    return output

  elif request.method == 'DELETE':
    vl.stop_temp = True
    return 'Stopped temperature change.'


@app.route('/on')
def on():
  asyncio.run(controller.bulb.update())
  asyncio.run(controller.bulb.turn_on())

@app.route('/off')
def off():
  asyncio.run(controller.bulb.update())
  asyncio.run(controller.bulb.turn_off())


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


