from collections import deque
from collections import namedtuple
import math
import random


TaskConfiguration = namedtuple('TaskConfiguration', ['grid_resolution',
                                                     'task_location',
                                                     'target_location',
                                                     'log_detail'])


# min x, min y, max x, max y; includes TARGET_WIDTH
TASK_BOUNDS = ((100, 100), (1530, 900))


def distance(p1, p2):
  """Euclidean distance between p1 and p2."""
  return math.sqrt(math.pow(p1[0]-p2[0], 2)+math.pow(p1[1]-p2[1], 2))


def round_to_nearest(val, multiple):
  """Rounds `val` to the nearest multiple of `multiple`."""
  return multiple * round(val / float(multiple))


def round_point(point, grid_width):
  """Rounds `point` to be aligned with a grid of `grid_width` resolution."""
  return (round_to_nearest(point[0], grid_width),
          round_to_nearest(point[1], grid_width))

def within_screen(location, screen):
  """Returns `true` if the point `location` is within `screen`.

  Args:
    location: An (x, y) point tuple.
    screen: An ((x_1, y_1), (x_2, y_2)) tuple of the top-left and bottom-right
      bounds of the screen.
  """
  return (screen[0][0] < location[0] < screen[1][0] and
          screen[0][1] < location[1] < screen[1][1])


def possible_targets(pointer, id, screen, width):
  """Returns a list of target positions that have the given `id` when pointed to from
  `pointer` (x, y) in the bounds of `screen`.
  """
  distance = width * (math.pow(2, id) - 1)
  diag_dist = distance / math.sqrt(2)  # a^2 + a^2 = c^2 (solved for a)

  all_targets = ((pointer[0] + distance, pointer[1]),  # E
                 (pointer[0] - distance, pointer[1]),  # W
                 (pointer[0], pointer[1] + distance),  # N
                 (pointer[0], pointer[1] - distance),  # S
                 (pointer[0] + diag_dist, pointer[1] + diag_dist),  # NE
                 (pointer[0] - diag_dist, pointer[1] + diag_dist),  # NW
                 (pointer[0] + diag_dist, pointer[1] - diag_dist),  # SE
                 (pointer[0] - diag_dist, pointer[1] - diag_dist))  # SW

  # Targets must fit within `screen`
  targets = list()
  for target in all_targets:
    if within_screen(target, screen) and target != pointer:
      # Clamp to neutral pixel grid
      t = round_point(target, width)
      targets.append(t)
  return targets


def generate_positive_condition(pointer,
                                screen,
                                target_id,
                                target_delta,
                                alignment,
                                tag):
  """Generates a condition for a target that is 'target_id' bits away from 'pointer'
  using normal pointing, but ('target_id' - 'target_delta') bits away using grid
  snapping. The targets are 'alignment' pixels wide, and must both fit in the bounds
  of 'screen'.
  """
  targets = possible_targets(pointer, target_id, screen, alignment)
  if not len(targets):
    return None

  target = random.choice(targets)

  offset = distance(pointer, target)
  is_diagonal = (abs(pointer[0] - target[0]) == abs(pointer[1] - target[1]))

  # Calculate the width of the target to create a ID delta of `target_delta`, this
  # becomes the width of the grid
  grid_id = -(target_delta - target_id)
  grid_width = offset / (math.pow(2, grid_id) - 1)

  grid_resolution = grid_width
  if is_diagonal:
    # Adjust for the fact that the grid_width is along an axis set by the targets.
    # This is aligned with the grid axes when the target is on a cardinal
    # direction, but for diagonal targets, the grid axis is offset by 45-degrees.
    # This is corrected by calculating what the grid resolution should be to
    # maintain a grid_width along the task axis.
    grid_resolution = grid_resolution / math.sqrt(2)

  # Adjust the location of the pointer/target so they are aligned with a grid that
  # starts at (0, 0)
  grid_offset = (pointer[0] % grid_resolution, pointer[1] % grid_resolution)
  pointer = (round(pointer[0] - grid_offset[0]), round(pointer[1] - grid_offset[1]))
  grid_offset = (target[0] % grid_resolution, target[1] % grid_resolution)
  target = (round(target[0] - grid_offset[0]), round(target[1] - grid_offset[1]))

  if int(target_delta) != target_delta:
    # Make sure targets are aligned with the pixel grid
    target = round_point(target, alignment)

  if not within_screen(target, screen) or not within_screen(pointer, screen):
    return None

  # Calculate actual ID
  real_neutral_id = math.log(distance(pointer, target) / alignment + 1, 2)

  # Closest distance using the grid
  # (This uses the grid along the task axis---the 'effective' grid.)
  grid_units = round(distance(pointer, target) / grid_width)
  grid_remainder = grid_units - (distance(pointer, target) / grid_width)

  if grid_remainder != 0:
    return None  # Too many accumulated rounding errors

  real_grid_id = math.log((grid_units * grid_width) / grid_width + 1, 2)

  return TaskConfiguration(grid_resolution,
                           pointer,
                           target,
                           ('POSITIVE', tag, target_id, target_delta, alignment,
                            real_neutral_id, real_grid_id))


def generate_split_condition(pointer, screen, target_id, grid_width, alignment, tag):
  targets = possible_targets(pointer, target_id, screen, alignment)
  if not len(targets):
    return None

  target = random.choice(targets)
  is_diagonal = (abs(pointer[0] - target[0]) == abs(pointer[1] - target[1]))

  grid_resolution = grid_width
  if is_diagonal:
    # Adjust for the fact that the grid_width is along an axis set by the targets.
    grid_resolution = grid_resolution / math.sqrt(2)

  # Adjust the location of the pointer so it is aligned with a grid that starts at
  # (0, 0)
  grid_offset = (pointer[0] % grid_resolution, pointer[1] % grid_resolution)
  pointer = (round(pointer[0] - grid_offset[0]),
             round(pointer[1] - grid_offset[1]))
  target = (round(target[0] - grid_offset[0]), round(target[1] - grid_offset[1]))

  # Make sure target is aligned with the pixel grid
  pointer = round_point(pointer, alignment)
  target = round_point(target, alignment)

  if not within_screen(target, screen) or not within_screen(pointer, screen):
    return None

  # Actual ID
  real_neutral_id = math.log(distance(pointer, target) / alignment + 1, 2)

  # Closest distance using the grid
  grid_units = round(distance(pointer, target) / grid_width)
  grid_distance = grid_units * grid_width
  remaining_distance = abs(grid_distance - distance(pointer, target))

  real_grid_id = (math.log(grid_distance / grid_width + 1, 2) +
                  math.log(remaining_distance / alignment + 1, 2))

  return TaskConfiguration(grid_resolution,
                           pointer,
                           target,
                           ('SPLIT', tag, target_id, grid_width, alignment,
                            real_neutral_id, real_grid_id))


def generate_negative_condition(pointer,
                                screen,
                                target_id,
                                target_delta,
                                alignment,
                                tag):
  """Generates a condition for a target that is 'target_id' bits away from 'pointer'
  using normal pointing, but winds up being ('target_id' - 'target_delta') bits away
  when grid snapping is used. The target always has a width of 'alignment' and must
  fit within the bounds of 'screen'.
  """
  targets = possible_targets(pointer, target_id, screen, alignment)
  if not len(targets):
      return None

  target = random.choice(targets)
  is_diagonal = (abs(pointer[0] - target[0]) == abs(pointer[1] - target[1]))

  real_id = -(target_delta - target_id)
  real_distance = alignment * math.pow(2, real_id) - 1

  # The closest grid point be 'real_distance' away from the target
  grid_width = real_distance * 2
  grid_resolution = grid_width
  if is_diagonal:
    # Adjust for the fact that the grid_width is along an axis set by the targets.
    grid_resolution = grid_resolution / math.sqrt(2)

  # The snapping grid starts at (0, 0), but the target should be halfway between
  # those grid points (aligned with an offset grid).
  grid_offset = (target[0] % grid_resolution, target[1] % grid_resolution)
  pointer = (round(pointer[0] - grid_offset[0]), round(pointer[1] - grid_offset[1]))
  target = (round(target[0] - grid_offset[0]), round(target[1] - grid_offset[1]))

  if is_diagonal:
    grid_offset = (grid_resolution / 2, grid_resolution / 2)
  else:
    if abs(pointer[0] - target[0]) > 0:  # Horizontal
      grid_offset = (grid_resolution / 2, 0)
    else:  # Vertical
      grid_offset = (0, grid_resolution / 2)

  pointer = (round(pointer[0] + grid_offset[0]),
             round(pointer[1] + grid_offset[1]))
  target = (round(target[0] + grid_offset[0]), round(target[1] + grid_offset[1]))

  # Make sure target is aligned with the pixel grid
  target = round_point(target, alignment)

  if not within_screen(target, screen) or not within_screen(pointer, screen):
    return None

  # Actual ID
  real_neutral_id = math.log(distance(pointer, target) / alignment + 1, 2)

  # Actual distance:
  real_grid_id = math.log(real_distance / alignment + 1, 2)

  return TaskConfiguration(grid_resolution,
                           pointer,
                           target,
                           ('NEGATIVE', tag, target_id, target_delta, alignment,
                            real_neutral_id, real_grid_id))


def generate_neutral_conditions(neutral_resolution,
                                target_id,
                                repetitions,
                                tag):
  screen = TASK_BOUNDS
  conditions = list()
  for _ in range(repetitions):
    # Generate neutral trial
    while True:
      start_x = random.randint(screen[0][0], screen[1][0])
      start_y = random.randint(screen[0][1], screen[1][1])
      pointer = (round_to_nearest(start_x, neutral_resolution),
                 round_to_nearest(start_y, neutral_resolution))

      neutral_id = target_id if target_id > 0 else -target_id

      targets = possible_targets(pointer, neutral_id, screen, neutral_resolution)
      if not targets:
        continue
      target = random.choice(targets)
      conditions.append(TaskConfiguration(neutral_resolution,
                                          pointer,
                                          target,
                                          ('NEUTRAL', tag, neutral_id, 0)))
      break
  return conditions


def generate_positive_conditions(neutral_resolution,
                                 target_id,
                                 target_delta,
                                 repetitions, tag):
  screen = TASK_BOUNDS
  conditions = list()
  for _ in range(repetitions):
    # Generate positive trial
    while True:
      start_x = random.randint(screen[0][0], screen[1][0])
      start_y = random.randint(screen[0][1], screen[1][1])
      pointer = (round_to_nearest(start_x, neutral_resolution),
                 round_to_nearest(start_y, neutral_resolution))

      neutral_id = target_id if target_id > 0 else -target_id

      if target_id < 0:
          cond = generate_split_condition(pointer,
                                          screen,
                                          -target_id,
                                          target_delta,  # grid_width
                                          neutral_resolution,
                                          tag)
      elif target_delta > 0:
        cond = generate_positive_condition(pointer,
                                           screen,
                                           target_id,
                                           target_delta,
                                           neutral_resolution,
                                           tag)

      if not cond:
        continue
      conditions.append(cond)
      break
  return conditions


def generate_negative_conditions(neutral_resolution,
                                 target_id,
                                 target_delta,
                                 repetitions, tag):
  screen = TASK_BOUNDS
  conditions = list()
  for _ in range(repetitions):
    # Generate negative trial
    while True:
      start_x = random.randint(screen[0][0], screen[1][0])
      start_y = random.randint(screen[0][1], screen[1][1])
      pointer = (round_to_nearest(start_x, neutral_resolution),
                 round_to_nearest(start_y, neutral_resolution))

      neutral_id = target_id if target_id > 0 else -target_id

      cond = generate_negative_condition(pointer,
                                         screen,
                                         target_id,
                                         target_delta,
                                         neutral_resolution,
                                         tag)

      if not cond:
        continue
      conditions.append(cond)
      break
  return conditions
