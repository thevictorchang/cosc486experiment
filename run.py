#!/usr/bin/env python

import os
import random
import re
import tkinter as tk

import grid_snapping
from grid_snapping_tasks import (TaskConfiguration,
                                 generate_neutral_conditions,
                                 generate_negative_conditions,
                                 generate_positive_conditions)
import logging
from master import MainWindow, SetupScreen, CompleteFrame


NEUTRAL_RESOLUTION = 4

PRACTICE_CONDITIONS = [
  # Neutral
  TaskConfiguration(NEUTRAL_RESOLUTION, (100, 100), (500, 500), ('PRACN',)),
  TaskConfiguration(NEUTRAL_RESOLUTION, (750, 200), (200, 500), ('PRACN',)),
  TaskConfiguration(NEUTRAL_RESOLUTION, (800, 600), (100, 100), ('PRACN',)),
  # Helpful
  # TaskConfiguration(50, (250, 300), (600, 500), ('PRACP',)),
  # TaskConfiguration(100, (1200, 200), (200, 100), ('PRACP',)),
  # TaskConfiguration(200, (800, 600), (200, 400), ('PRACP',)),
  # # Mostly helpful
  # TaskConfiguration(50, (100, 100), (512, 512), ('PRACS',)),
  # TaskConfiguration(100, (600, 200), (612, 312), ('PRACS',)),
  # TaskConfiguration(50, (800, 600), (312, 112), ('PRACS',)),
  # # Unhelpful
  # TaskConfiguration(50, (527, 527), (528, 528), ('PRACH',)),
  # TaskConfiguration(200, (690, 690), (700, 700), ('PRACH',)),
  # TaskConfiguration(100, (454, 624), (452, 652), ('PRACH',)),
]

# Format:
#  [Tasks] [Group Name]_[Series Name]
#  "Series Name" should either be "A" or "B" to indicate hypothesised preferred
#  or not preferred.

TEST_CONDITIONS = [('2C ControlN_A'), ('2P ControlN_B')]

CONTROL_CONDITIONS = [
 ('8C ControlN_A', '8N ControlN_B'),
 ('8P ControlP_A', '8C ControlP_B'),
]

EXPERIMENTAL_CONDITIONS_1 = [
 ('12C+4P +EndStart_A', '4P+12C +EndStart_B'),            # +End   vs. +Start
 ('12C+4P +EndMid_A', '6C+4P+6C +EndMid_B'),      # +End   vs. +Mid
 ('4P+12C +StartMid_A', '6C+4P+6C +StartMid_B'),  # +Start vs. +Mid
]

EXPERIMENTAL_CONDITIONS_2 = [
 ('4N+12C -StartEnd_A', '12C+4N -StartEnd_B'),            # -Start vs. -End
 ('6C+4N+6C -EndMid_A', '12C+4N -EndMid_B'),      # -End   vs. -Mid
 ('6C+4N+6C -StartMid_A', '4N+12C -StartMid_B'),  # -Start vs. -Mid
]


NR = NEUTRAL_RESOLUTION
BASE_ID = 5  # Base/neutral ID
EXP_ID = 6 # Base experimental ID
POS_DELTA = 4  # Delta for pure positive conditions
NEG_DELTA = -1  # Delta for pure negative conditions
SPLIT_WIDTH = 224  # Grid width for split conditions for id=6 delta=2


def rotate(l,n):
  n = n % len(l)
  return l[n:] + l[:n]

def parse_condition(design):
  """Parses a design (e.g. '10CN+4P') into a list of experimental tasks."""
  name = design.split(' ')[1]
  chunks = design.split(' ')[0].split('+')
  condition_tasks = []

  for chunk in chunks:
    parts = re.findall('(\d+)(\w+)', chunk)[0]
    count, task_type = int(parts[0]), parts[1]

    tasks = []
    for task in task_type:
      if task == 'C':
        tasks += generate_neutral_conditions(NR, EXP_ID, count, name)
      elif task == 'P':
        tasks += generate_positive_conditions(NR, EXP_ID, POS_DELTA, count, name)
      elif task == 'N':
        tasks += generate_negative_conditions(NR, EXP_ID, NEG_DELTA, count, name)
    random.shuffle(tasks)
    condition_tasks.extend(tasks)
  return condition_tasks

def shuffle_conditions(conditions):
  all_conditions = list()
  for condition_pair in conditions:
    condition = [parse_condition(condition_pair[0]),
                 parse_condition(condition_pair[1])]
    random.shuffle(condition)
    all_conditions.append(condition)
  random.shuffle(all_conditions)
  return all_conditions

def main():
  os.system('xset m default')
  os.system("xinput --set-prop "
            "'Logitech USB Optical Mouse' 'Device Accel Constant Deceleration' 3")

  root = tk.Tk()
  root.tk_setPalette(background='white')

  root.wm_attributes('-fullscreen', 1)
  #root.geometry('1000x900-0+1')

  main_window = MainWindow(root)

  log_dir = os.path.join(os.path.dirname(__file__), 'run-logs')

  def complete_experiment():
    complete = CompleteFrame(main_window)
    main_window.navigate_to(complete)

  # Callback for WelcomeScreen
  def start_experiment(subject):
    subject, logger = logging.MakeLogger(subject if subject is not None else None,
                                         log_dir)

    # Generate conditions
    conditions = list()  # List of lists of task configurations
    all_conditions = shuffle_conditions(CONTROL_CONDITIONS)
    # if subject % 2 == 0:
    #   all_conditions.extend(shuffle_conditions(EXPERIMENTAL_CONDITIONS_1))
    # else:
    #   all_conditions.extend(shuffle_conditions(EXPERIMENTAL_CONDITIONS_2))
    
    for condition in all_conditions:
      conditions.extend(condition)

    controller = grid_snapping.Controller(main_window,
                                          subject,
                                          logger,
                                          NEUTRAL_RESOLUTION,
                                          PRACTICE_CONDITIONS,
                                          conditions,
                                          complete_experiment)
    controller.start()

  SetupScreen(main_window, start_experiment)

  root.mainloop()


if __name__ == '__main__':
  main()
