import time
import asyncio

from flask import Flask, request, render_template

from . import controller
from .controller import vlc
from .controller.brightness import Brightness
from .controller.temperature import ColorTemperature

# from .logger import log

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('home.html', vlc=vlc)



@app.route('/on')
def on():
  asyncio.run(controller.bulb.update())
  asyncio.run(controller.bulb.turn_on())
  return 'on'

@app.route('/off')
def off():
  asyncio.run(controller.bulb.update())
  asyncio.run(controller.bulb.turn_off())
  return 'off'


# @app.route('/lamp/override', methods=['GET'])
@app.route('/lamp', methods=['GET', 'DELETE'])
def lamp():
  if request.method == 'GET':
    vlc.new_override()
    return 'new override'
  if request.method == 'DELETE':
    vlc.disengage()
    return 'returning to nvl'
  return 'what'



@app.route('/brightness', methods=['POST', 'DELETE'])
@app.route('/brightness/<target>')
@app.route('/brightness/<target>/<duration>')
@app.route('/brightness/<target>/<duration>/<start_value>')
def brightness(target=None, duration=0, start_value=None):
  if vlc.is_normal_mode():
    vlc.new_override()

  curr_brightness = vlc.ovl.brightness

  if request.method == 'GET':
    target = int(target) if target else None
    start_value = int(start_value) if start_value else None

    if curr_brightness.running:
      curr_brightness.should_stop = True
      time.sleep(1)
    curr_brightness.change(target, int(duration), start_value)
    return str(target)
  
  elif request.method == 'DELETE':
    curr_brightness.should_stop = True
    return 'Stopping current brightness change.'


@app.route('/temp', methods=['POST', 'DELETE'])
@app.route('/temp/<target>')
@app.route('/temp/<target>/<duration>')
@app.route('/temp/<target>/<duration>/<start_value>')
def color_temp(target=None, duration=0, start_value=None):
  if vlc.is_normal_mode():
    vlc.new_override()

  curr_color_temp = vlc.ovl.color_temp

  if request.method == 'GET':
    target = int(target) if target else None
    start_value = int(start_value) if start_value else None

    curr_color_temp.change(target, int(duration), start_value)
    return str(target)

  elif request.method == 'DELETE':
    curr_color_temp.should_stop = True
    return 'Stopping current color temp change.'



def change(instance: Brightness, target=None, duration=0, start_value=None):
  if vlc.is_normal_mode():
    vlc.new_override()

  if request.method == 'GET':
    target = int(target) if target else None
    start_value = int(start_value) if start_value else None

    if instance.running:
      instance.should_stop = True
      time.sleep(1)
    instance.change(target, int(duration), start_value)
    return str(target)
  
  elif request.method == 'DELETE':
    instance.should_stop = True
    return 'Stopping current brightness change.'