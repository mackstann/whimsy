# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, signal, select

from Xlib.display import Display

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

def main_loop(wm, **options):
    delay = options.get('resolution', 10) / 1000.0
    while 1:
        signal.alarm(20)
        select.select([wm.dpy], [], [], delay)
        wm.pull_all_pending_events()
        wm.handle_all_pending_events()
        signal.alarm(0)

def init(**options):
    set_display_env()
    return window_manager(Display())

def run(wm, **options):
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

