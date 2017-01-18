import tkinter as tk
import sys
#from screeninfo import get_monitors

class MainWindow(tk.Frame):
  """Master window that contains all experimental screens."""
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    self.pack(fill=tk.BOTH, expand=True)

  def navigate_to(self, frame):
    """Removes all child frames except for `frame`."""
    for child in self.winfo_children():
      if child != frame:
        child.destroy()


class SetupScreen(tk.Frame):
  def __init__(self, master, next_callback):
    tk.Frame.__init__(self, master)

    assert next_callback is not None
    self._next_callback = next_callback

    #if self._check_entry_condition():
      #participant meets entry conditions (so far just screen resolution of 1080)
    next = tk.Button(self, text='Start Practice', state='normal')
    next.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    next.bind('<Button-1>', lambda e: self._next_clicked(e))
    # else:
    #   message = tk.Label(self, text="Your screen resolution doesn't meet the requirements for this experiment. \n"
    #                                 "Please connect to a 1080p monitor.")
    #   message.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    #self._entry = tk.Entry(self, width=5)
    #self._entry.place(in_=next, relx=0.5, anchor=tk.S)

    self.pack(fill=tk.BOTH, expand=True)

  def _next_clicked(self, e):
    #subject = self._entry.get().strip()
    #if len(subject) == 0:
    #  self._next_callback(None)
    #else:
    #  self._next_callback(int(subject))
    self._next_callback(None)

  #check if screen reolution is 1080 and if a mouse is connected
  def _check_entry_condition(self):

    #resolution check...
    for m in get_monitors():
      if ('1080' in str(m)):
        return True

    return False

    #mouse check...








class CompleteFrame(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    self.pack(fill=tk.BOTH, expand=True)

    entry = tk.Button(self, text='Close')
    entry.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    entry.bind('<Button-1>', lambda e: sys.exit(0))

    label = tk.Label(self, text='Experiment Complete\nThank you!')
    label.place(in_=entry, relx=0.5, anchor=tk.S)


