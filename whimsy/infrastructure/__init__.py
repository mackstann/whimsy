# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

"""
this module is meant to mediate between the window manager and the "real
world," handling the boring runtime stuff such as signal handlers and shell
environment and a main loop.  the core window manager code ideally should be
totally ignorant about these things.

wm = infrastructure.init()
infrastructure.run(wm)
"""

import os, signal, traceback, select, errno, time

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

def lenient_select(r, w, x, timeout):
    # sigchld for example will interrupt select() and cause an unhandled
    # socket.error exception.
    try:
        return select.select(r, w, x, timeout)
    except select.error, e:
        if e[0] == errno.EINTR:
            return [], [], []
        raise

def main_loop(wm):
    # at this time there is no particular reason to call select() up to 100
    # times per second -- it could just block on the X event fd.  but if timers
    # were ever to be implemented in whimsy (i.e. execute some action 5 seconds
    # after i hit this key), then this approach will let us do it.  you can
    # currently do a delay with execute("sleep N; ..."), but this is limited to
    # shell commands, obviously.
    hz100 = 1.0/100
    while True:
        signal.alarm(20)
        for i in xrange(500): # so we only make alarm() system call every 5s or so
            lenient_select([wm.dpy], [], [], hz100)
            wm.pull_all_pending_events()
            wm.handle_all_pending_events()
        signal.alarm(0)

def init():
    set_display_env()
    return window_manager(Display())

def run(wm):
    def alrm(*a):
        raise RuntimeError('froze!')
    signal.signal(signal.SIGALRM, alrm)
    signal.signal(signal.SIGCHLD, wait_signal_handler)
    wm.manage()
    try:
        main_loop(wm)
    except KeyboardInterrupt:
        wm.shutdown()
        raise SystemExit

