import cx_Freeze
import sys

import os

os.environ['TCL_LIBRARY'] = "C:\Python36\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "C:\\Python36\\tcl\\tk8.6"


base = None

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("framing_experiment.py", base=base)]

cx_Freeze.setup(
    name = "COSC486 Experiment",
    options = {"build_exe": {"packages":["tkinter", "screeninfo", "logging"], "include_files": ["grid_snapping.py", "grid_snapping_tasks.py", "experiment_logging.py", "master.py", "survey.py"]}},
    version = "0.01",
    description = "COSC486 Experiment",
    executables = executables
    )
