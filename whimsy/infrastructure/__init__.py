# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, signal, traceback

from Xlib.display import Display
import select

from whimsy.log import *
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
    while 1:
        signal.alarm(20)

        resuming_select([wm.dpy], [], [], delay)
        wm.pull_all_pending_events()
        wm.handle_all_pending_events()

        # temporary super ugly kludge for monitor.sh to be able to kill us if we hang
        import datetime as dt
        n = dt.datetime.now()
        file('now.txt', 'w').write(
            ('%04d%02d%02d %02d:%02d\n' % (n.year, n.month, n.day, n.hour, n.minute))+
            ('%04d%02d%02d %02d:%02d\n' % (n.year, n.month, n.day, n.hour, n.minute-1))+
            ('%04d%02d%02d %02d:%02d\n' % (n.year, n.month, n.day, n.hour, n.minute+1))
        )
        signal.alarm(0)

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
    try:
        main_loop(wm, **options)
    except KeyboardInterrupt:
        wm.shutdown()
        raise SystemExit

