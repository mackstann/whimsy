# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, signal

from Xlib import display
from Xlib.support.connect import get_display

from whimsy.signals import publisher
from whimsy.models.window_manager import window_manager
from whimsy.controllers.x_event_controller import x_event_controller
from whimsy.controllers.tick_controller import tick_controller

def wait_signal_handler(*args):
    try:
        os.waitpid(-1, os.WNOHANG | os.WUNTRACED)
    except OSError:
        pass

class main(object):
    def __init__(self):
        os.environ['DISPLAY'] = get_display(None)[0]

        self.dpy    = display.Display()
        self.hub    = publisher()
        self.wm     = window_manager(self.hub, self.dpy)
        self.xec    = x_event_controller(self.hub, self.dpy)
        self.ticker = tick_controller(self.hub)

        self.hub.defaults['wm'] = self.wm
        self.hub.defaults['hub'] = self.hub

        self.hub.register('tick', self.xec.select_and_emit_all)

    def run(self):
        signal.signal(signal.SIGCHLD, wait_signal_handler)
        signal.signal(signal.SIGTERM, lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGINT,  lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGPIPE, lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGUSR1, lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGUSR2, lambda signum, frame: self.ticker.stop())

        self.wm.manage()
        self.ticker.tick_forever()

