# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

"""
currently in upheaval
"""

import os, errno

def get_display_name():
    from Xlib.support.connect import get_display
    return get_display(None)[0]

def set_display_env():
    os.environ['DISPLAY'] = get_display_name()

def wait_signal_handler(*args):
    try:
        os.waitpid(-1, os.WNOHANG | os.WUNTRACED)
    except OSError:
        return

