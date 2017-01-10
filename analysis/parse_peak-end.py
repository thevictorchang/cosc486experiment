#!/usr/bin/env python

import os.path
import sys

import numpy

def is_preferred_condition(name):
  return name.split('_')[1] == 'A'
  
def condition_name(name):
  return name.split('_')[0]

# File header
print('\t'.join(['subject',
       'condition',
       'first',
       'a_t',
       'b_t',
       'a_r',
       'b_r',
       'pref']))

for file_name in sys.argv[1:]:
  file = open(file_name, 'r')

  in_practise = True
  # Expect files to be named 'subject-0.txt', and extract the '0'.
  subject_id = int(os.path.split(file_name)[1].split('.')[0].split('-')[1])

  control_times = list()  # Trial times for control task
  exp_times = list()    # Trial times for experimental task
  control_rating = 0  # Rating for control task
  exp_rating = 0  # Rating for experimental task
  control_first = None  # Did they do the control first or second?

  is_control = False  # In control task?
  condition = ''  # Condition name

  first_mousedown = False  # Made a mousedown in the trial yet?
  start_time = 0  # Trial start time

  for line in file:
    line = line.strip()
    line = line.split('\t')

    timestamp = float(line[0])
    event = line[1]
    params = line[2:]

    # Skip practise trials at the start of the log
    if in_practise and event != 'ENDPRACTISE':
      continue
    elif event == 'ENDPRACTISE':
      in_practise = False

    if event == 'TASKCONFIG' and is_preferred_condition(params[1]):
      # Start of hypothesised-preferred trials
      is_control = True
      first_mousedown = False
      if control_first is None:
        control_first = True

      condition = condition_name(params[1])
    
    elif event == 'TASKCONFIG' and not is_preferred_condition(params[1]):
      # Start of hypothesised-not-preferred trials
      is_control = False
      first_mousedown = False
      if control_first is None:
        control_first = False

      condition = condition_name(params[1])
        
    elif event == 'MOUSEDOWN' and not first_mousedown:
      first_mousedown = True
      start_time = timestamp
    
    elif event == 'COMPLETE' and is_control:
      duration = timestamp - start_time
      control_times.append(duration)

    elif event == 'COMPLETE' and not is_control:
      duration = timestamp - start_time
      exp_times.append(duration)

    elif event == 'RATING' and is_control:
      control_rating = int(params[0])

    elif event == 'RATING' and not is_control:
      exp_rating = int(params[0])

    elif event == 'PREFERENCE':
      # Did they do the 'A' or 'B' condition first?
      first = "A"
      if not control_first:
        first = "B"

      pref = int(params[0])  # 1 = First, 0 = Second
      pref_str = None

      # Figure out which condition ('A' or 'B') they preferred
      if control_first and pref == 1:
        pref_str = "A"
      elif control_first and pref == 0:
        pref_str = "B"
      elif not control_first and pref == 1:
        pref_str = "B"
      elif not control_first and pref == 0:
        pref_str = "A"

      print('%d\t%s\t%s\t%.2f\t%.2f\t%d\t%d\t%s' % (
        subject_id,
        condition,
        first,
        numpy.sum(control_times),
        numpy.sum(exp_times),
        control_rating,
        exp_rating,
        pref_str
      ))

      # Reset parameters
      control_times = list()
      exp_times = list()
      control_first = None
