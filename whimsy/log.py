# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, sys, logging

# public stuff

critical = logging.critical
error = logging.error
warning = logging.warning
info = logging.info
debug = logging.debug

#######################################

_logging_options = dict(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
)

def _set_to_filename(fn):
    _logging_options['filename'] = fn
    _logging_options['filemode'] = 'w'
    if 'stream' in _logging_options:
        del _logging_options['stream']

def _set_to_stream(stream):
    if 'filename' in _logging_options:
        del _logging_options['filename']
    if 'filemode' in _logging_options:
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
        _initial_warning = ("could not create ``%s''. logging to stderr." % _whimsy_dir)

#_set_to_filename(os.path.join(_whimsy_dir, 'log'))
_set_to_stream(sys.stderr)

logging.basicConfig(**_logging_options)

if _initial_warning:
    warn(_initial_warning)

