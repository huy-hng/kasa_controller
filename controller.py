import time
import math
import asyncio

from kasa import SmartBulb

from logger import log

SINGLE_CHANGE_DUR = 0.12

bulb = SmartBulb('192.168.188.26')

################
#region Helpers#
################
def perceived2actual_brightness(perceived):
  return round((perceived ** 2) / 100)

def actual2perceived_brightness(actual_brightness):
  return round(math.sqrt(actual_brightness*100))

def round_to_nearest_100(x, base=100):
  return int(base * round(float(x)/base))

def get_diff(curr_val, target_val):
  diff = target_val - curr_val
  if diff > 0:
    cond = lambda curr_val: curr_val < target_val
  else:
    cond = lambda curr_val: curr_val > target_val

  log.debug(f'{diff=}')
  return diff, cond

def calc_sleep_dur(duration, amount_of_steps):
  expected_change_dur = SINGLE_CHANGE_DUR * amount_of_steps
  sleep_dur = duration - expected_change_dur

  if sleep_dur < 0:
    sleep_dur = 0

  single_sleep_dur = sleep_dur / amount_of_steps

  log.debug(f'sleep_dur={round(sleep_dur, 2)}')
  log.debug(f'expected_change_dur={round(expected_change_dur, 2)}')
  log.debug(f'expected_change_dur={round(expected_change_dur, 2)}')
  return single_sleep_dur, sleep_dur

async def transition(curr_value, target_value, cond, fn, step_size, single_sleep_dur):
  t0 = time.perf_counter()
  while cond(curr_value):
    curr_value += step_size

    if not cond(curr_value):
      # check that curr_value doesnt overshoot target_value
      curr_value = target_value

    await fn(curr_value)

    time.sleep(single_sleep_dur)

  t1 = time.perf_counter() - t0
  # log.debug(f'actual_change_dur={round(t1-sleep_dur, 4)}')
  log.debug(f'actual_complete_dur={round(t1, 4)}')
#endregion Helpers
################



###################
#region Brightness#
###################
async def change_brightness(target_value: int, duration: int, start_value: int=None):
  await bulb.turn_on()
  await bulb.update()

  log.warning('')
  log.debug(f'{start_value=}')
  log.debug(f'curr_value={bulb.brightness}')
  log.debug(f'{target_value=}')
  log.debug(f'{duration=}')

  if duration==0:
    await set_brightness(target_value)
    return
  elif start_value is not None:
    # use bulb.set_brightness bc set_brightness has a turn off feature
    await bulb.set_brightness(perceived2actual_brightness(start_value))
    
  await transition_bright(target_value, duration)


async def set_brightness(value):
  turn_off = False
  if value == 0:
    value = 1
    turn_off = True

  actual_brightness = perceived2actual_brightness(value)
  log.debug(f'perceived_brightness={value}|{actual_brightness=}')
  await bulb.set_brightness(actual_brightness)

  if turn_off:
    log.info(f'brightness is 0, turning lamp off')
    time.sleep(0.2)
    await bulb.turn_off()


async def transition_bright(target_value: int, duration: int):
  curr_value = actual2perceived_brightness(bulb.brightness)

  diff, cond = get_diff(curr_value, target_value)
  if diff == 0:
    if curr_value == 0:
      await bulb.turn_off()
      log.info(f'turning off')
    else:
      log.info(f'exiting, no difference')
    return # return when theres no change to make

  amount_of_steps, step_size = get_steps(duration, diff)
  single_sleep_dur, sleep_dur = calc_sleep_dur(duration, amount_of_steps)
  
  await transition(curr_value, target_value, cond, set_brightness, step_size, single_sleep_dur)

  # t0 = time.perf_counter()
  # while cond(curr_value):
  #   curr_value += step_size

  #   if not cond(curr_value):
  #     # check that curr_value doesnt overshoot target_value
  #     curr_value = target_value

  #   await set_brightness(curr_value)

  #   time.sleep(single_sleep_dur)

  # t1 = time.perf_counter() - t0
  # log.debug(f'actual_change_dur={round(t1-sleep_dur, 4)}')
  # log.debug(f'actual_complete_dur={round(t1, 4)}')


def get_steps(duration, diff):
  step_size = (diff * SINGLE_CHANGE_DUR) / (duration)
  
  if abs(step_size) < 2:
    step_size = 2 if step_size > 0 else -2
  elif step_size < 0:
    step_size = math.floor(step_size)
  else:
    step_size = math.ceil(step_size)

  log.debug(f'{step_size=}')
  amount_of_steps = math.ceil(diff / step_size)
  return amount_of_steps, step_size

#endregion Brightness
###################



####################
#region Temperature#
####################
async def change_temperature(target_value: int, duration: int, start_value: int=None):
  await bulb.turn_on()
  await bulb.update()

  if duration==0:
    await set_color_temp(target_value)
    return
  elif start_value is not None:
    await set_color_temp(start_value)
    
  await transition_color_temp(target_value, duration)


async def set_color_temp(value):
  await bulb.set_color_temp(value)


async def transition_color_temp(target_t: int, duration:int):
  target_temp = 38 * target_t + 2700
  curr_temp = bulb.color_temp

  diff, cond = get_diff(curr_temp, target_temp)
  if diff == 0:
    return # return when theres no change to make

  #region calc step_size
  step_size = (diff * SINGLE_CHANGE_DUR) / duration

  if abs(step_size) < 100:
    step_size = 100 if step_size > 0 else -100

  step_size = round_to_nearest_100(step_size)
  log.debug(f'{step_size=}')
  #endregion

  amount_of_steps = math.ceil(diff / step_size)
  single_sleep_dur, sleep_dur = calc_sleep_dur(duration, amount_of_steps)


  t0 = time.perf_counter()
  while cond(curr_temp):
    curr_temp += step_size

    if not cond(curr_temp):
      # check that curr_temp doesnt overshoot target_temp
      curr_temp = target_temp

    await bulb.set_color_temp(curr_temp)

    time.sleep(single_sleep_dur)
  
  t1 = time.perf_counter() - t0
  log.debug(f'actual_change_dur={round(t1-sleep_dur, 4)}')
  log.debug(f'actual_complete_dur={round(t1, 4)}')
#endregion Temperature
####################



async def main():
  await bulb.update()
  b = 0 if bulb.brightness == 100 else 100
  c = 0 if bulb.color_temp == 6500 else 100

  #TODO: since 1-15 is all the same brightness, improve it somehow
  await change_brightness(15, 1)
  # await change_temperature(c, 1)


asyncio.run(main())