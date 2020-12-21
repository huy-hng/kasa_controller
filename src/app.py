import os

from flask import Flask, request, render_template

from .controller import vlc, profiles
from .logger import log
# pylint: disable=logging-fstring-interpolation

app = Flask(__name__)

@app.route('/')
def home():
  # TODO: move to react
  return render_template('home.html', vlc=vlc) # FIX: vulneralbility



@app.route('/on')
def on():
  vlc.active_vlamp.on = True
  return 'on'

@app.route('/off')
def off():
  vlc.active_vlamp.on = False
  return 'off'


@app.route('/lamp/<lamp_id>')
def lamp(lamp_id=None):
  lamp_id = int(lamp_id)
  if lamp_id == 0:
    vlc.disengage()
  else:
    vlc.override()
  return f'lamp changed to {lamp_id}'

@app.route('/override')
@app.route('/override/<duration>')
def override(duration=0):
  vlc.override(int(duration))
  return '0'

@app.route('/disengage/')
@app.route('/disengage/<duration>')
def disengage(duration=1):
  duration = int(duration)
  log.info(f'disengaging with the duration of {duration}')
  vlc.disengage(duration)
  return '0'

########
#region# brightness
########
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
  vlc.override(0, False)
  return change_brightness(vlc.ovl, request.method, target, duration, start_value)

  
@app.route('/nvl/brightness', methods=['DELETE'])
@app.route('/nvl/brightness/<target>')
@app.route('/nvl/brightness/<target>/<duration>')
@app.route('/nvl/brightness/<target>/<duration>/<start_value>')
def nvl_brightness(target=None, duration=0, start_value=None):
  return change_brightness(vlc.nvl, request.method, target, duration, start_value)

###########
#endregion# brightness
########

########
#region# color_temp
########
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
  vlc.override(0, False)
  return change_color_temp(vlc.ovl, request.method, target, duration, start_value)


@app.route('/nvl/temp', methods=['DELETE'])
@app.route('/nvl/temp/<target>')
@app.route('/nvl/temp/<target>/<duration>')
@app.route('/nvl/temp/<target>/<duration>/<start_value>')
def nvl_color_temp(target=None, duration=0, start_value=None):
  return change_color_temp(vlc.nvl, request.method, target, duration, start_value)

###########
#endregion# color_temp
########

@app.route('/profile/<p>')
@app.route('/profile/<p>/<vlamp>')
@app.route('/profile/<p>/<vlamp>/<args>')
def profile(p, vlamp=None):
  if vlamp == 'ovl':
    vlc.override()

  fn = profiles.profiles.get(p)
  if fn is not None:
    fn() if vlamp is None else fn(vlc.ovl)
    return f'Executed {p}'
  return f'Profile "{p}" not found.'

@app.route('/when_sunset')
def when_sunset():
  start, duration = profiles.get_sunset()
  return f'start={start.hour}:{start.minute} duration={round(duration.seconds/60, 2)}'



#############
#region logs#
#############
@app.route('/debug')
def debug():
  files = os.listdir('./logs/debug')
  files.sort()
  with open(f'./logs/debug/{files[-1]}') as f:
    return f'./logs/debug/{files[-1]} \n\n<pre>{f.read()}</pre>'

@app.route('/info')
def info():
  files = os.listdir('./logs/info')
  files.sort()
  with open(f'./logs/info/{files[-1]}') as f:
    return f'<pre>{f.read()}</pre>'

##########
#endregion
#############