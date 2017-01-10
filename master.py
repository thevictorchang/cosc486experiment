import tkinter as tk
import sys


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

    next = tk.Button(self, text='Start Practice')
    next.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    next.bind('<Button-1>', lambda e: self._next_clicked(e))

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


class CompleteFrame(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    self.pack(fill=tk.BOTH, expand=True)

    entry = tk.Button(self, text='Close')
    entry.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    entry.bind('<Button-1>', lambda e: sys.exit(0))

    label = tk.Label(self, text='Experiment Complete\nThank you!')
    label.place(in_=entry, relx=0.5, anchor=tk.S)


