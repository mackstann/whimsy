# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2006.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

import os, sys, logging

# public stuff

def critical(msg): logging.critical(msg)
def error(msg): logging.error(msg)
def warning(msg): logging.warning(msg)
def info(msg): logging.info(msg)
def debug(msg): logging.debug(msg)

# end public stuff ######################################

_logging_options = dict(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    filename=os.path.expanduser('~/.whimsy/log'),
    filemode='w'
)

def _set_to_filename(fn):
    _logging_options['filename'] = fn
    _logging_options['filemode'] = 'w'
    del _logging_options['stream']

def _set_to_stream(stream):
    del _logging_options['filename']
    del _logging_options['filemode']
    _logging_options['stream'] = stream


_initial_warning = ''
_whimsy_dir = os.path.expanduser('~/.whimsy')

try:
    os.mkdir(_whimsy_dir)
except OSError, e:
    _strerror = e.strerror.lower()
    if 'file exists' in _strerror:
        # that's fine
        pass
    elif 'permission denied' in _strerror:
        _set_to_stream(sys.stderr)
        _initial_warning = ("could not create ``%s''. logging to stderr." %
                _whimsy_dir)

#_set_to_filename(os.path.join(_whimsy_dir, 'log'))
_set_to_stream(sys.stderr)

logging.basicConfig(**_logging_options)

if _initial_warning:
    warn(_initial_warning)

