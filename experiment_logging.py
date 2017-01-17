import os
import os.path
import sys
import time


LOG_FILE_DIRECTORY = os.path.join(os.path.dirname(__file__), 'logs')
LOG_FILE_PREFIX = 'subject-'
LOG_FILE_EXTENSION = '.txt'


class Logger(object):
  def __init__(self, file):
    assert file is not None
    self._file = file

  def Close(self):
    self._file.close()

  def WriteLine(self, command, *params):
    assert command is not None

    timestamp = time.time()  # Seconds since the epoch
    param_str = '\t'.join([str(p) for p in params])
    if len(param_str) > 0:
      param_str = '\t' + param_str

    self._file.write('%f\t%s%s\n' % (timestamp, str(command), param_str))
    self._file.flush()


def MakeLogger(subject_number=None,
               directory=LOG_FILE_DIRECTORY,
               file_prefix=LOG_FILE_PREFIX,
               file_extension=LOG_FILE_EXTENSION):
  """Creates a new log file and returns a tuple of the subject number and Logger."""
  if not os.path.exists(directory):
    os.makedirs(directory)

  if subject_number is None:
    # Find any existing log files in `directory`
    files = os.listdir(directory)
    files = [f for f in files if (f.startswith(file_prefix) and
                                   f.endswith(file_extension))]
    # Strip prefix and extension
    files = [f[len(file_prefix):-len(file_extension)] for f in files]
    files = [int(f) for f in files]

    if len(files) == 0:
      subject_number = 1
    else:
      subject_number = max(files) + 1

  file_name = file_prefix + str(subject_number) + file_extension
  file_path = os.path.join(directory, file_name)

  old_mask = os.umask(0)
  f = os.open(file_path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, int('0666', 8))
  f = os.fdopen(f, 'a')
  os.umask(old_mask)

  return (subject_number, Logger(f))
