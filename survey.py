import os.path
import tkinter as tk

BASE_DIR = os.path.dirname(__file__)


class IntraRatingFrame(tk.Frame):
  def __init__(self, master, logger, progress, continue_callback):
    tk.Frame.__init__(self, master)
    self.pack()

    self._logger = logger
    self._continue_callback = continue_callback

    self._rating = tk.IntVar()
    self._rating.set(0)

    tk.Frame(self, height=100).pack()  # Top Padding

    tk.Label(self,
             wraplength=500,
             text='How annoying was that set of dragging trials?\n'
             'From -5 (extremely frustrating) to +5 (extremely satisfying).',
             pady=10).pack()

    tk.Scale(self,
             from_=-5,
             to=5,
             length=400,
             tickinterval=5,
             orient=tk.HORIZONTAL,
             variable=self._rating).pack()

    wrap_frame = tk.Frame(self)
    image = tk.PhotoImage(file=os.path.join(BASE_DIR, 'negative.gif'))
    label = tk.Label(wrap_frame, image=image, width=180, anchor=tk.W)
    label.image = image
    label.pack(side=tk.LEFT)

    image = tk.PhotoImage(file=os.path.join(BASE_DIR, 'neutral.gif'))
    label = tk.Label(wrap_frame, image=image, width=180, anchor=tk.W)
    label.image = image
    label.pack(side=tk.LEFT)

    image = tk.PhotoImage(file=os.path.join(BASE_DIR, 'positive.gif'))
    label = tk.Label(wrap_frame, image=image)
    label.image = image
    label.pack(side=tk.LEFT)
    wrap_frame.pack()

    tk.Frame(self, height=30).pack()  # Padding

    self._next = tk.Button(self,
                           text=progress,
                           command=lambda *args: self._continue_clicked())
    self._next.pack(side=tk.BOTTOM)

  def _continue_clicked(self):
    self._logger.WriteLine('RATING', self._rating.get())
    self._continue_callback()


class OnOrOffFrame(tk.Frame):
  def __init__(self, master, logger, progress, continue_callback, subject_id):
    tk.Frame.__init__(self, master)
    self.pack()

    self._logger = logger
    self._continue_callback = continue_callback

    tk.Frame(self, height=100).pack()  # Top Padding

    # The 'Continue' button becomes enabled this is 'True'
    self._touched_posneg = False

    self._pos_neg = tk.IntVar()
    self._pos_neg.set(-1)  # Matches neither
    self._pos_neg.trace('w', lambda *args: self._posneg_changed())



    framing_question = ""
    if (subject_id % 2 == 0):
        framing_question = "(SUBJECT ID is EVEN so this will be a POSITIVELY FRAMED question) \n" \
                           "If you were to repeat this set of exercises, would you have the Grid\n Snapping feature turned on?"
    else:
        framing_question = "(SUBJECT ID is ODD so this will be a NEGATIVELY FRAMED question) \n" \
                            "If you were to repeat this set of exercises, would you have the Grid Snapping feature turned off?"


    tk.Label(self,
             wraplength=500,
             text=framing_question).pack()

    # tk.Button(self, text="BUTTON 1 FOR ON/OFF").pack()
    # tk.Button(self, text="BUTTON 2 FOR ON/OFF").pack()


    #Preferences: value '1' is leaving grid snap ON, value '0' if turning grid snap OFF

    wrap_frame = tk.Frame(self, pady=10)

    if (subject_id % 2 == 0):

        tk.Radiobutton(wrap_frame,
                       text='Yes',
                       variable=self._pos_neg,
                       value=1,
                       padx=10).pack(side=tk.LEFT)
        tk.Radiobutton(wrap_frame,
                       text='No',
                       variable=self._pos_neg,
                       value=0).pack(side=tk.LEFT)
    else:
        tk.Radiobutton(wrap_frame,
                       text='Yes',
                       variable=self._pos_neg,
                       value=0,
                       padx=10).pack(side=tk.LEFT)
        tk.Radiobutton(wrap_frame,
                       text='No',
                       variable=self._pos_neg,
                       value=1).pack(side=tk.LEFT)


    wrap_frame.pack()

    tk.Frame(self, height=30).pack()  # Padding

    self._next = tk.Button(self,
                           text=progress,
                           state=tk.DISABLED,
                           command=lambda *args: self._continue_clicked())
    self._next.pack(side=tk.BOTTOM)




  def _posneg_changed(self):
    # Enable the 'Continue' button once they've selected an option
    self._next.config(state=tk.NORMAL)


  def _continue_clicked(self):
    print('PREFERENCE' + str(self._pos_neg.get()))
    self._logger.WriteLine('PREFERENCE', self._pos_neg.get())
    self._continue_callback()


class InterRatingFrame(tk.Frame):
  def __init__(self, master, logger, progress, continue_callback):
    tk.Frame.__init__(self, master)
    self.pack()

    self._logger = logger
    self._continue_callback = continue_callback

    tk.Frame(self, height=100).pack()  # Top Padding

    # The 'Continue' button becomes enabled this is 'True'
    self._touched_posneg = False

    self._pos_neg = tk.IntVar()
    self._pos_neg.set(-1)  # Matches neither
    self._pos_neg.trace('w', lambda *args: self._posneg_changed())

    tk.Label(self,
             wraplength=500,
             text='If you were to repeat one of the last two sets of trials,\n'
             'which would you prefer to do?').pack()

    wrap_frame = tk.Frame(self, pady=10)
    tk.Radiobutton(wrap_frame,
                   text='First',
                   variable=self._pos_neg,
                   value=1,
                   padx=10).pack(side=tk.LEFT)
    tk.Radiobutton(wrap_frame,
                   text='Second',
                   variable=self._pos_neg,
                   value=0).pack(side=tk.LEFT)
    wrap_frame.pack()

    tk.Frame(self, height=30).pack()  # Padding

    self._next = tk.Button(self,
                           text=progress,
                           state=tk.DISABLED,
                           command=lambda *args: self._continue_clicked())
    self._next.pack(side=tk.BOTTOM)




  def _posneg_changed(self):
    # Enable the 'Continue' button once they've selected an option
    self._next.config(state=tk.NORMAL)

  def _continue_clicked(self):
    self._logger.WriteLine('PREFERENCE', self._pos_neg.get())
    self._continue_callback()
