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
  # TODO: move to react
  return render_template('home.html', vlc=vlc) # FIX: vulneralbility



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
# @app.route('/lamp', methods=['GET', 'DELETE'])
@app.route('/lamp/<lamp_id>')
def lamp(lamp_id=None):
  vlc.set_active(int(lamp_id))
  return f'lamp changed to {lamp_id}'



def change_brightness(vl, method, target, duration, start_value):
  if method == 'GET':
    target = int(target) if target else None
    start_value = int(start_value) if start_value else None

    vl.brightness.change(target, int(duration), start_value)
    return str(target)
  
  elif method == 'DELETE':
    vl.brightness.should_stop = True
    return 'Stopping current brightness change.'



@app.route('/brightness', methods=['DELETE'])
@app.route('/brightness/<target>')
@app.route('/brightness/<target>/<duration>')
@app.route('/brightness/<target>/<duration>/<start_value>')
def brightness(target=None, duration=0, start_value=None):
  if vlc.is_normal_mode():
    vlc.set_active(1)
  return change_brightness(vlc.ovl, request.method, target, duration, start_value)

  
@app.route('/nvl/brightness', methods=['DELETE'])
@app.route('/nvl/brightness/<target>')
@app.route('/nvl/brightness/<target>/<duration>')
@app.route('/nvl/brightness/<target>/<duration>/<start_value>')
def nvl_brightness(target=None, duration=0, start_value=None):
  return change_brightness(vlc.nvl, request.method, target, duration, start_value)



def change_color_temp(vl, method, target, duration, start_value):
  if method == 'GET':
    target = int(target) if target else None
    start_value = int(start_value) if start_value else None

    vl.color_temp.change(target, int(duration), start_value)
    return str(target)

  elif method == 'DELETE':
    vl.color_temp.should_stop = True
    return 'Stopping current color temp change.'


@app.route('/temp', methods=['DELETE'])
@app.route('/temp/<target>')
@app.route('/temp/<target>/<duration>')
@app.route('/temp/<target>/<duration>/<start_value>')
def color_temp(target=None, duration=0, start_value=None):
  if vlc.is_normal_mode():
    vlc.set_active(1)
  return change_color_temp(vlc.ovl, request.method, target, duration, start_value)


@app.route('/nvl/temp', methods=['DELETE'])
@app.route('/nvl/temp/<target>')
@app.route('/nvl/temp/<target>/<duration>')
@app.route('/nvl/temp/<target>/<duration>/<start_value>')
def nvl_color_temp(target=None, duration=0, start_value=None):
  return change_color_temp(vlc.nvl, request.method, target, duration, start_value)
