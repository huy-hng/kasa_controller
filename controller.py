import time
import math
import asyncio

from kasa import SmartBulb


bulb = SmartBulb('192.168.188.26')


def perceived_brightness_arr(step_size, reverse=False):
  perc_bright = 1
  measured_bright = 14
  arr = []

  while perc_bright < 100:
    perc_bright = perceived_to_measured_brightness(measured_bright)
    if perc_bright > 100:
      perc_bright = 100
    arr.append(perc_bright)
    measured_bright += step_size

  if reverse:
    arr.reverse()

  return arr

def perceived_to_measured_brightness(brightness):
  return round((brightness ** 2) / 100)


def round_to_nearest_100(x, base=100):
  return int(base * round(float(x)/base))



async def set_brightness(brightness):
  await bulb.set_brightness(brightness)
  await bulb.update()


async def set_color_temp(temp):
  # takes about 0.14sec to execute
  await bulb.set_color_temp(temp)


async def transition_color_temp(target_t: int, duration:int):
  await bulb.update()

  single_change_dur = 0.14

  target_temp = 38 * target_t + 2700
  curr_temp = bulb.color_temp

  diff = target_temp - curr_temp
  if diff == 0:
    # return when theres no change to make
    return
  elif diff > 0:
    cond = lambda: curr_temp < target_temp
  else:
    cond = lambda: curr_temp > target_temp

  #region calc step_size
  step_size = (diff * single_change_dur) / duration

  if abs(step_size) < 100:
    step_size = 100 if step_size > 0 else -100

  step_size = round_to_nearest_100(step_size)
  print(f'{step_size=}')
  #endregion

  amount_of_steps = math.ceil(diff / step_size)
  expected_change_dur = single_change_dur * amount_of_steps

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


async def transition_brightness(target_b: int, duration: int):
  """ 
  brightness from 0 to 100
  
  duration in seconds
  """
  await bulb.update()
  single_change_dur = 0.15
  curr_b = bulb.brightness

  diff = target_b - curr_b
  if diff == 0:
    # return when theres no change to make
    return
  elif diff > 0:
    cond = lambda: curr_b < target_b
  else:
    cond = lambda: curr_b > target_b

  step_size = (diff * single_change_dur) / (duration)

  print(f'{step_size=}')
  
  if abs(step_size) < 1:
    step_size = 1 if step_size > 0 else -1

  if step_size < 0:
    step_size = math.floor(step_size)
  else:
    step_size = math.ceil(step_size)

  print(f'{step_size=}')

  amount_of_steps = math.ceil(diff / step_size)
  expected_change_dur = single_change_dur * amount_of_steps

  #region calc sleep dur
  sleep_dur = duration - expected_change_dur
  if sleep_dur < 0: sleep_dur = 0
  single_sleep_dur = sleep_dur / amount_of_steps
  #endregion
  
  t0 = time.perf_counter()
  while cond():
    curr_b += step_size

    if not cond():
      # check that curr_b doesnt overshoot target_b
      curr_b = target_b

    await bulb.set_brightness(perceived_to_measured_brightness(curr_b))

    time.sleep(single_change_dur)

  print(f'{sleep_dur=}')
  print(f'{expected_change_dur=}')
  
  print('actual dur:', round(time.perf_counter() - t0, 4))
  print('expected dur:', expected_change_dur + sleep_dur)
