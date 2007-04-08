# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

import os, sys, signal, traceback, time

from Xlib.display import Display
from Xlib import X, XK
import select

from whimsy.log import *
from whimsy import event, modifiers
from whimsy.event_handling.builtins import *
from whimsy.actions.builtins import *
from whimsy.client import managed_client
from whimsy.window_manager import window_manager

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

def resuming_select(r, w, x, timeout):
    rr, rw, rx = [], [], []
    while not rr and not rw and not rx:
        try:
            rr, rw, rx = select.select(r, w, x, timeout)
        except select.error, e:
            if 'interrupted system call' not in e.args[1].lower():
                raise
        else:
            return rr, rw, rx

def main_loop(wm, **options):
    delay = options.get('resolution', 10) / 1000.0
    try:
        while 1:
            signal.alarm(20)

            resuming_select([wm.dpy], [], [], delay)
            wm.pull_all_pending_events()
            wm.handle_all_pending_events()

            import datetime as dt
            n = dt.datetime.now()
            file('now.txt', 'w').write(
                ('%04d%02d%02d %02d:%02d\n' % (n.year, n.month, n.day, n.hour, n.minute))+
                ('%04d%02d%02d %02d:%02d\n' % (n.year, n.month, n.day, n.hour, n.minute-1))+
                ('%04d%02d%02d %02d:%02d\n' % (n.year, n.month, n.day, n.hour, n.minute+1))
            )
            signal.alarm(0)
            # anything periodic goes here, like timers (not implemented yet)
    except KeyboardInterrupt:
        raise SystemExit

def init(**options):
    set_display_env()
    return window_manager(Display())

def run(wm, **options):
    import signal, traceback
    def alrm(*a):
        raise RuntimeError('froze!')
    signal.signal(signal.SIGALRM, alrm)
    signal.signal(signal.SIGCHLD, wait_signal_handler)
    wm.manage()
    main_loop(wm, **options)

