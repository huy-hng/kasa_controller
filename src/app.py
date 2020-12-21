import os

from flask import Flask, request, render_template, jsonify

from .periodic_runner.change_detection import check_changes
from .controller import vlc, profiles
from .logger import log
# pylint: disable=logging-fstring-interpolation

app = Flask(__name__)

@app.route('/')
def home():
  # TODO: move to react
  return render_template('home.html', vlc=vlc, environment=os.getenv('ENVIRONMENT')) # FIX: vulneralbility


@app.route('/check_for_changes')
def check_for_changes():
  check_changes()


@app.route('/set_active_lamp/<id_>')
def set_active_lamp(id_):
  try:
    id_ = int(id_)
  except Exception as e:
    log.error(f"id has to be an int and not '{id_}'")
    return jsonify(success=False), 400
  
  vlc.set_active_lamp(id_)
  return jsonify(success=True)

@app.route('/get/<value>')
def get_value(value):
  if value == 'brightness':
    return str(vlc.active_vlamp.brightness.perceived)
  elif value == 'color_temp':
    return str(vlc.active_vlamp.color_temp.percent)


@app.route('/on')
def on():
  vlc.active_vlamp.on = True
  return 'on'

@app.route('/off')
def off():
  vlc.active_vlamp.on = False
  return 'off'


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



@app.route('/<vlamp_id>/brightness', methods=['DELETE'])
@app.route('/<vlamp_id>/brightness/<target>')
@app.route('/<vlamp_id>/brightness/<target>/<duration>')
@app.route('/<vlamp_id>/brightness/<target>/<duration>/<start_value>')
def brightness(vlamp_id, target=None, duration=0, start_value=None):
  vlc.override(0, False)
  return change_brightness(vlc.tom, request.method, target, duration, start_value)

  
@app.route('/nvl/brightness', methods=['DELETE'])
@app.route('/nvl/brightness/<target>')
@app.route('/nvl/brightness/<target>/<duration>')
@app.route('/nvl/brightness/<target>/<duration>/<start_value>')
def nvl_brightness(target=None, duration=0, start_value=None):
  return change_brightness(vlc.nom, request.method, target, duration, start_value)

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
  return change_color_temp(vlc.tom, request.method, target, duration, start_value)


@app.route('/nvl/temp', methods=['DELETE'])
@app.route('/nvl/temp/<target>')
@app.route('/nvl/temp/<target>/<duration>')
@app.route('/nvl/temp/<target>/<duration>/<start_value>')
def nvl_color_temp(target=None, duration=0, start_value=None):
  return change_color_temp(vlc.nom, request.method, target, duration, start_value)

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
    fn() if vlamp is None else fn(vlc.tom)
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