import os

from flask import Flask, request, render_template, jsonify

# from .periodic_runner.change_detection import check_changes

from .controller import vlc, profiles
from src.logger import log
# pylint: disable=logging-fstring-interpolation

app = Flask(__name__)

@app.route('/')
def home():
  # TODO: move to react
  return render_template('home.html', vlc=vlc, environment=os.getenv('ENVIRONMENT')) # FIX: vulneralbility


# @app.route('/check_for_changes')
# def check_for_changes():
#   check_changes()


@app.route('/set_active_vlamp/<id_>')
def set_active_vlamp(id_=None):
  try:
    id_ = int(id_)
  except Exception as e:
    log.error(f"id has to be an int and not '{id_}'")
    return jsonify(success=False), 400
  
  vlc.set_active_vlamp(id_)
  return jsonify(success=True)

@app.route('/handlers')
def handlers():
  return str(len(log.handlers))

@app.route('/<vlamp_id>/on')
def on(vlamp_id):
  vlamp = vlc.get_vlamp_by_id(vlamp_id)
  vlamp.on = True
  return f'Turning {vlamp.name} on'

@app.route('/<vlamp_id>/off')
def off(vlamp_id):
  vlamp = vlc.get_vlamp_by_id(vlamp_id)
  vlamp.on = False
  return f'Turning {vlamp.name} off'


@app.route('/<vlamp_id>/brightness', methods=['GET', 'DELETE'])
@app.route('/<vlamp_id>/color_temp', methods=['GET', 'DELETE'])
def choose_action(vlamp_id=0):
  if vlamp_id == 0:
    return

  vlamp = vlc.get_vlamp_by_id(vlamp_id)

  if vlc.active_vlamp.id != 2:
    vlc.set_active_vlamp(vlamp.id, 0)

  action = request.path.split('/')[2]
  if action == 'brightness':
    vlamp_value = vlamp.brightness
  else:
    vlamp_value = vlamp.color_temp

  return handle_method(vlamp_value, request)

def handle_method(vlamp_value, req):
  if req.method == 'GET':

    if req.args.get('target') is None:
      return str(vlamp_value.value)
    return set_value(vlamp_value, req)

  elif request.method == 'DELETE':
    vlamp_value.should_stop = True
    return 'Stopped brightness change.'

def set_value(vlamp_value, req):
  target = req.args.get('target')
  duration = req.args.get('duration')
  start = req.args.get('start')

  log.debug(f'{target=} {duration=} {start=}')
  try:  
    target = int(target) if target else None
    duration = int(duration) if duration else 0
    start = int(start) if start else None
  except ValueError:
    error_message = f"Values need to convertable to an int and not '{target}', '{duration}' or '{start}'"
    log.warning(error_message)
    return error_message

  vlamp_value.change(target, duration, start)
  
  start_text = ''
  if start:
    start_text = f' from {start}'
  return f'Changing value{start_text} to {target} in {duration} seconds.'


@app.route('/<vlamp_id>/profile/<profile>')
def launch_profile(vlamp_id, profile):
  vlamp = vlc.get_vlamp_by_id(vlamp_id)

  fn = profiles.profiles.get(profile)
  if fn is not None:
    fn() if vlamp is None else fn(vlc.tom)
    return f'Executed {profile}'
  return f'Profile "{profile}" not found.'



@app.route('/state')
def state():
  # return jsonify({vlamp.id: vlamp.state for vlamp in vlc.vlamps})
  return jsonify(vlc.active_vlamp.state)


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