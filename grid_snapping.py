import math
import random
import tkinter as tk

from grid_snapping_tasks import *
from survey import InterRatingFrame, IntraRatingFrame, OnOrOffFrame

TARGET_WIDTH = 50  # Visual width (not pointng width)

class TaskScreen(tk.Frame):
  """Widget for a single grid snapping movement trial."""
  def __init__(self,
               master,
               logger,
               complete_callback,
               neutral_resolution=1,
               configuration=None,
               mode_label=None):
    """Sets up the trial.

    Args:
      master: The parent frame to contain this widget.
      logger: The logger to send output to.
      complete_callback: A function to call when the task has been successfully
        completed.
      neutral_resolution: The resolution of dragging actions when grid snapping
        is disabled/off.
      configuration: A dictionary containing:
        grid_resolution: The resolution of the grid.
        task_location: The (x, y) location of the starting position.
        target_location: The (x, y) location of the target position.
        log_detail: A description of the configuration for the logger.
      mode_label: An optional label to display at the top of the widget.
    """
    tk.Frame.__init__(self, master)
    self.pack(fill=tk.BOTH, expand=True)

    self._logger = logger
    self._logger.WriteLine('NEWTASK')
    self._complete_callback = complete_callback
    self._neutral_resolution = neutral_resolution

    self._is_selected = False  # Is the object currently selected?
    self._initial_snap = False  # Has the object been snapped to the grid once?
    self._drag_snapping = False  # Is the drag movement in snapping mode?
    self._is_dragging = False

    self._show_grid = False  # Draw a visible grid?

    if mode_label is not None:
      self._mode_label = tk.Label(self, text=mode_label)
      self._mode_label.pack()

    self._canvas = tk.Canvas(self, bg='white')
    self._canvas.pack(fill=tk.BOTH, expand=True)

    self._object_size = (TARGET_WIDTH, TARGET_WIDTH)
    # Some defaults...
    self._target_location = (500, 500)
    self._task_location = (110, 110)
    self._grid_resolution = (100, 100)

    if configuration is not None:
      self.set_grid_resolution(configuration.grid_resolution)
      self.set_task_location(*configuration.task_location)
      self.set_target_location(*configuration.target_location)
      self._logger.WriteLine('TASKCONFIG', *configuration.log_detail)

    self._draw_grid()
    self._draw()

    self._canvas.bind('<Button-1>', lambda e: self._mouse_down(e))
    self._canvas.bind('<B1-Motion>', lambda e: self._mouse_dragged(e))
    self._canvas.bind('<ButtonRelease-1>', lambda e: self._mouse_up(e))
    self._canvas.bind('<Configure>', lambda e: self._canvas_configure(e))

  def set_target_location(self, x, y):
    self._target_location = (x, y)
    self._logger.WriteLine('TARGET', x, y)
    self._draw()

  def set_task_location(self, x, y):
    self._task_location = (x, y)
    self._is_selected = False
    self._logger.WriteLine('TASK', x, y)
    self._draw()

  def set_grid_resolution(self, x, y=None):
    if y is None:
      y = x
    self._grid_resolution = (x, y)
    self._logger.WriteLine('RESOLUTION', x, y)
    self._draw_grid()
    self._draw()

  def _canvas_configure(self, event):
    self._draw_grid()
    self._draw()

  def _draw_grid(self):
    if not self._show_grid:
      return

    self._canvas.delete(tk.ALL)
    # Draw the grid
    if (self._grid_resolution[0] > self._neutral_resolution or
        self._grid_resolution[1] > self._neutral_resolution):
      (x, y) = (0, 0)
      while x <= self._canvas.winfo_width():
        self._canvas.create_line(x, 0,
                                 x, self._canvas.winfo_height(), fill='grey90')
        x += self._grid_resolution[0]

      while y <= self._canvas.winfo_height():
        self._canvas.create_line(0, y,
                                 self._canvas.winfo_width(), y, fill='grey90')
        y += self._grid_resolution[1]

  def _draw(self):
    self._canvas.delete('task')

    # Offset the target rectangle by 1 px so the task rectangle can sit within it
    self._canvas.create_rectangle(self._target_location[0] - 1,
                                  self._target_location[1] - 1,
                                  self._target_location[0] + self._object_size[0],
                                  self._target_location[1] + self._object_size[1],
                                  tags='task')

    if self._task_location == self._target_location:
      task_fill = 'green'
    elif self._is_selected:
      task_fill = 'blue'
    else:
      task_fill = 'black'

    self._canvas.create_rectangle(self._task_location[0], self._task_location[1],
                                  self._task_location[0] + self._object_size[0],
                                  self._task_location[1] + self._object_size[1],
                                  fill = task_fill, width=0, tags='task')
    self._canvas.update()

  def _mouse_down(self, event):
      self.focus()
      self._logger.WriteLine('MOUSEDOWN', event.x, event.y)
      # Mouse down inside the task rectangle?
      if (event.x > self._task_location[0] and
          event.x < (self._task_location[0] + self._object_size[0]) and
          event.y > self._task_location[1] and
          event.y < (self._task_location[1] + self._object_size[1])):
        self._is_dragging = True

        # Select 'snapping' mode if the control key is not down, or there hasn't been
        # an initial snap yet
        if event.state & 0x04 == 0 or not self._initial_snap:  # 0x04 == Control key
          self._drag_snapping = True
          self._logger.WriteLine('SNAPPING', True)
        else:
          self._drag_snapping = False
          self._logger.WriteLine('SNAPPING', False)

        self._drag_mouse_origin = (event.x, event.y)
        self._drag_task_origin = self._task_location
        self._logger.WriteLine('STARTDRAG')
      else:
        self._is_dragging = False
      self._draw()

  def _mouse_up(self, event):
    self._logger.WriteLine('MOUSEUP', event.x, event.y)
    self._is_selected = False
    self._is_dragging = False
    self._draw()

    if self._task_location == self._target_location:
      self._logger.WriteLine('COMPLETE')
      self._complete_callback()

  def _mouse_dragged(self, event):
    #self._logger.WriteLine('MOUSEMOVE', event.x, event.y)
    if not self._is_dragging:
      return

    self._is_selected = True
    #self._logger.WriteLine('MOUSEDRAG', event.x, event.y)

    # The offset of the drag event from the initial one
    offset = (event.x - self._drag_mouse_origin[0],
              event.y - self._drag_mouse_origin[1])
    #self._logger.WriteLine('OFFSET', offset[0], offset[1])

    # Apply the snapping function to the updated location
    new_location = (self._drag_task_origin[0] + offset[0],
                    self._drag_task_origin[1] + offset[1])
    #self._logger.WriteLine('LOCATION', new_location[0], new_location[1])

    # Round to the closest multiple of the grid resolution
    if self._drag_snapping:
      resolution = self._grid_resolution
    else:
      resolution = (self._neutral_resolution, self._neutral_resolution)

    new_location = (resolution[0] * round(float(new_location[0])/resolution[0]),
                    resolution[1] * round(float(new_location[1])/resolution[1]))
    new_location = (round(new_location[0]), round(new_location[1]))
    #self._logger.WriteLine('SNAPPED', new_location[0], new_location[1])
    self._initial_snap = True

    # Clamp the location to the canvas bounds
    canvas_size = (self._canvas.winfo_width(), self._canvas.winfo_height())
    new_location = (min(max(0, new_location[0]),
                        canvas_size[0] - self._object_size[0]),
                    min(max(0, new_location[1]),
                        canvas_size[1] - self._object_size[1]))

    self._task_location = new_location
    #self._logger.WriteLine('MOVELOC', self._task_location[0], self._task_location[1])
    self._draw()


class BreakFrame(tk.Frame):
  """Widget with a single 'Continue' button that calls a callback when clicked.

  Used to separate conditions.
  """
  def __init__(self, master, logger, continue_callback, timeout=0):
    tk.Frame.__init__(self, master)
    self.pack(fill=tk.BOTH, expand=True)

    self._logger = logger
    self._continue_callback = continue_callback
    self._timeout = timeout

    if timeout > 0:
      label = tk.Label(self, wraplength=500,
                       text='The next set of tasks will begin in...')
      label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
      self._label = tk.Label(self, wraplength=500,
                             text=str(timeout))
      self._label.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
      self.after(1000, self._countdown)

      self._next = tk.Button(self, text='Begin First Set', state=tk.DISABLED)
    else:
      # No timeout
      self._next = tk.Button(self, text='Begin First Set')
    self._next.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    self._next.bind('<Button-1>', lambda e: self._continue_clicked(e))

  def _countdown(self):
    self._timeout -= 1
    self._label.configure(text=str(self._timeout))

    if self._timeout == 0:
      self._next.configure(state=tk.NORMAL)
    else:
      self.after(1000, self._countdown)

  def _continue_clicked(self, e):
    self._logger.WriteLine('CONTINUE')
    self._continue_callback()


class Controller(object):
  """Creates a series of conditions and transitions through them."""
  def __init__(self,
               window,
               subject_id,
               logger,
               neutral_resolution,
               practice_conditions,
               conditions,
               complete_callback):
    """Sets up a grid snapping experiment.

    Args:
      window: The parent window that should contain the experimental view.
      subject_id: Numerical identifier for the subject being run.
      logger: The logger to send output to.
      neutral_resolution: The default pointing resolution to be used when there is no
        grid snapping.
      practice_conditions: A list of TaskConfigurations that will be run through as
        subject practice.
      conditions: A list of lists of TaskConfigurations.
      complete_callback: A function to call when the experiment has been completed.
    """
    self._window = window
    self._logger = logger
    self._complete_callback = complete_callback
    self._subject_id = subject_id

    self._neutral_resolution = neutral_resolution
    self._practise_conditions = practice_conditions
    self._completed_practise = False

    self._conditions = conditions
    self._condition = conditions.pop(0)
    self._condition_count = 0

  def start(self):
    self._logger.WriteLine('STARTGRID')
    self._logger.WriteLine('STARTPRACTISE')
    self.trial_complete()

  def trial_complete(self):
    """Triggers the next condition."""
    # In practise mode?
    if not self._completed_practise:
      if len(self._practise_conditions):
        print("you just did a trial congrats")
        # Next practise trial/condition is available
        config = self._practise_conditions.pop(0)

        task = TaskScreen(self._window,
                          self._logger,
                          lambda: self.trial_complete(),
                          self._neutral_resolution,
                          config,
                          'Practice Set')
        self._window.navigate_to(task)
      else:
        # End practise session
        self._completed_practise = True
        self._logger.WriteLine('ENDPRACTISE')
        task = BreakFrame(self._window,
                          self._logger,
                          lambda: self.trial_complete())
        self._window.navigate_to(task)

    # Are there real conditions remaining?
    elif len(self._condition) or len(self._conditions):

      if len(self._condition):
        # Continue current condition
        config = self._condition.pop(0)
        #self._logger.WriteLine('EXPERIENCE', config.log_detail[0])

        if self._condition_count == 0:
            model_label = 'First Set'
        elif self._condition_count == 1:
            model_label = 'Second Set'
        elif self._condition_count == 2:
            model_label = 'Third Set'

        task = TaskScreen(self._window,
                          self._logger,
                          lambda: self.trial_complete(),
                          self._neutral_resolution,
                          config,
                          model_label)
        self._window.navigate_to(task)
      elif len(self._conditions):
        self._condition_count += 1
        # Between conditions...
        # First, show a break screen]
        # if self._condition_count % 2 == 0:
        #     frame = OnOrOffFrame(self._window, self._logger, "HELLO WORLD LOL", self.rating_complete())
        # else:
        #     frame = OnOrOffFrame(self._window, self._logger, "HELLO WORLD LOL", self.rating_complete())
        if self._condition_count % 2 == 0:
          frame = OnOrOffFrame(self._window, self._logger, "Complete Set", lambda: self.break_screen(), self._subject_id)
          print("Subject_id is: " + str(self._subject_id))
          print("Config is: " + str(TaskScreen.config))
          # frame = IntraRatingFrame(self._window,
          #                          self._logger,
          #                          'Complete Set',
          #                          lambda: self.rating_complete())
        else:
          frame = OnOrOffFrame(self._window, self._logger, "Complete Set", lambda: self.break_screen(), self._subject_id)
          print("Subject_id is: " + str(self._subject_id))
          #print("Config is: " + str(TaskScreen.config(self)))

        self._condition = self._conditions.pop(0)
        self._window.navigate_to(frame)

    else:
      # Experiment complete; ask for condition rating first
      frame = OnOrOffFrame(self._window, self._logger, "Complete Set", lambda: self._complete_callback(), self._subject_id)
      self._window.navigate_to(frame)
    #print self._condition[0].log_detail

  def break_screen(self):
    frame = BreakFrame(self._window,
                       self._logger,
                       lambda: self.trial_complete(),
                       2) #change back to 7 when not testing
    self._window.navigate_to(frame)

  def rating_complete(self):
    #if not len(self._condition) and not len(self._conditions):
      # Experiment complete
    frame = InterRatingFrame(self._window,
                           self._logger,
                           'Continue',
                           lambda: self._complete_callback())
    # else:
    #   frame = InterRatingFrame(self._window,
    #                            self._logger,
    #                            'Continue',
    #                            lambda: self.break_screen())
    self._window.navigate_to(frame)

