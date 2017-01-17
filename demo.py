#!/usr/bin/env python

import os
import random

import tkinter as tk

import grid_snapping
from grid_snapping_tasks import (TaskConfiguration,
                                 generate_neutral_conditions,
                                 generate_positive_conditions)
import experiment_logging
from master import MainWindow, SetupScreen, CompleteFrame


NEUTRAL_RESOLUTION = 4

PRACTICE_CONDITIONS = [
  # Neutral
  TaskConfiguration(NEUTRAL_RESOLUTION, (100, 100), (500, 500), ('PRACN',)),
  TaskConfiguration(NEUTRAL_RESOLUTION, (750, 200), (200, 500), ('PRACN',)),
  # Helpful
  TaskConfiguration(50, (250, 300), (600, 500), ('PRACP',)),
  TaskConfiguration(100, (600, 200), (200, 100), ('PRACP',)),
  # Mostly helpful
  TaskConfiguration(50, (100, 100), (512, 512), ('PRACS',)),
  TaskConfiguration(100, (600, 200), (612, 312), ('PRACS',)),
  # Unhelpful
  TaskConfiguration(200, (690, 690), (700, 700), ('PRACH',)),
  TaskConfiguration(100, (454, 624), (452, 652), ('PRACH',)),

]

def rotate(l,n):
  n = n % len(l)
  return l[n:] + l[:n]


def main():
  #os.system('xset m default')
  #os.system("xinput --set-prop "
  #          "'Logitech USB Optical Mouse' 'Device Accel Constant Deceleration' 3")

  root = tk.Tk()
  root.tk_setPalette(background='white')

  #root.wm_attributes('-fullscreen', 1)
  root.geometry('1000x900-0+1')

  main_window = MainWindow(root)

  log_dir = os.path.join(os.path.dirname(__file__), 'DEMO')

  # Generate conditions
  NR = NEUTRAL_RESOLUTION
  BASE_ID = 5  # Base/neutral ID
  EXP_ID = 6 # Base experimental ID
  POS_DELTA = 4  # Delta for pure positive conditions
  SPLIT_WIDTH = 224  # Grid width for split conditions for id=6 delta=2

  def complete_experiment():
    complete = CompleteFrame(main_window)
    main_window.navigate_to(complete)

  # Callback for WelcomeScreen
  def start_experiment(subject):
    subject, logger = experiment_logging.MakeLogger(subject if subject is not None else None,
                                         log_dir)

    conditions = list()  # List of lists of task configurations

    # Preliminary comparisons
    conditions = [
      generate_neutral_conditions(NR, EXP_ID, 2, 'PRE1_NEUTRAL'),
      generate_positive_conditions(NR, EXP_ID, POS_DELTA, 2, 'PRE1_POSITIVE')
    ]

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
