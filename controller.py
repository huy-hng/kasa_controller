import time
import math
import asyncio

from kasa import SmartBulb

SINGLE_CHANGE_DUR = 0.12

bulb = SmartBulb('192.168.188.26')

################
#region Helpers#
################
def perceived_to_measured_brightness(brightness):
  return round((brightness ** 2) / 100)

def round_to_nearest_100(x, base=100):
  return int(base * round(float(x)/base))
#endregion Helpers
################



###################
#region Brightness#
###################
async def change_brightness(target_value: int, duration: int, start_value: int=None):
  await bulb.turn_on()
  await bulb.update()

  if duration==0:
    await set_brightness(target_value)
    return
  elif start_value is not None:
    # use bulb.set_brightness bc set_brightness has a turn off feature
    await bulb.set_brightness(start_value)
    
  await transition_brightness(target_value, duration)


async def set_brightness(value):
  turn_off = False
  if value == 0:
    value = 1
    turn_off = True

  # t0 = time.perf_counter()
  await bulb.set_brightness(perceived_to_measured_brightness(value))
  # print(round(time.perf_counter() - t0, 4))

  if turn_off:
    time.sleep(1)
    await bulb.turn_off()


async def transition_brightness(target_b: int, duration: int):
  curr_b = bulb.brightness

  diff = target_b - curr_b
  if diff == 0:
    return # return when there is no change to make
  elif diff > 0:
    cond = lambda: curr_b < target_b
  else:
    cond = lambda: curr_b > target_b

  amount_of_steps, step_size = get_steps(duration, diff)
  single_sleep_dur, sleep_dur = calc_single_sleep_dur(duration, amount_of_steps)
  
  t0 = time.perf_counter()
  while cond():
    curr_b += step_size

    if not cond():
      # check that curr_b doesnt overshoot target_b
      curr_b = target_b

    await set_brightness(curr_b)

    time.sleep(single_sleep_dur)

  t1 = time.perf_counter() - t0
  print('actual_change_dur:', round(t1-sleep_dur, 4))
  print('actual_complete_dur:', round(t1, 4))


def get_steps(duration, diff):
  step_size = (diff * SINGLE_CHANGE_DUR) / (duration)
  
  if abs(step_size) < 2:
    step_size = 2 if step_size > 0 else -2
  elif step_size < 0:
    step_size = math.floor(step_size)
  else:
    step_size = math.ceil(step_size)

  print(f'{step_size=}')
  amount_of_steps = math.ceil(diff / step_size)
  return amount_of_steps, step_size


def calc_single_sleep_dur(duration, amount_of_steps):
  expected_change_dur = SINGLE_CHANGE_DUR * amount_of_steps
  sleep_dur = duration - expected_change_dur

  if sleep_dur < 0:
    sleep_dur = 0

  single_sleep_dur = sleep_dur / amount_of_steps

  print('sleep_dur:', round(sleep_dur, 2))
  print('expected_change_dur:', round(expected_change_dur, 2))
  print('expected_complete_dur:', expected_change_dur + sleep_dur)
  return single_sleep_dur, sleep_dur
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

  diff = target_temp - curr_temp
  if diff == 0: # return when theres no change to make
    return
  elif diff > 0:
    cond = lambda: curr_temp < target_temp
  else:
    cond = lambda: curr_temp > target_temp

  #region calc step_size
  step_size = (diff * SINGLE_CHANGE_DUR) / duration

  if abs(step_size) < 100:
    step_size = 100 if step_size > 0 else -100

  step_size = round_to_nearest_100(step_size)
  print(f'{step_size=}')
  #endregion

  amount_of_steps = math.ceil(diff / step_size)
  expected_change_dur = SINGLE_CHANGE_DUR * amount_of_steps

  #region calc sleep dur
  sleep_dur = duration - expected_change_dur
  if sleep_dur < 0: sleep_dur = 0
  single_sleep_dur = sleep_dur / (amount_of_steps - 1)
  #endregion
  

  t0 = time.perf_counter()
  while cond():
    curr_temp += step_size

    if not cond():
      # check that curr_temp doesnt overshoot target_temp
      curr_temp = target_temp

    await bulb.set_color_temp(curr_temp)

    time.sleep(single_sleep_dur)

  print(f'{sleep_dur=}')
  print(f'{expected_change_dur=}')
  
  print('actual dur:', round(time.perf_counter() - t0, 4))
  print('expected dur:', expected_change_dur + sleep_dur)
#endregion Temperature
####################



async def main():
  await bulb.update()
  b = 0 if bulb.brightness == 100 else 100
  await change_brightness(b, 1)


asyncio.run(main())