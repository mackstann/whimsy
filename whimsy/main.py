# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, signal, logging, logging.handlers

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

        self.dpy    = dpy    = display.Display()
        self.hub    = hub    = publisher()
        self.wm     = wm     = window_manager(hub, dpy)
        self.xec    = xec    = x_event_controller(hub, dpy)
        self.ticker = ticker = tick_controller(hub)

        self.hub.defaults['wm'] = wm
        self.hub.defaults['hub'] = hub

        # if a tick hasn't happened for 10 seconds we've definitely gotten stuck
        self.hub.register('tick', lambda **kw: signal.alarm(10))
        self.hub.register('tick', xec.select_and_emit_all)

        self.log_filename = None

    def setup_logging(self):
        root_logger = logging.getLogger('')
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

        if not self.log_filename:
            return

        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(
            logging.handlers.RotatingFileHandler(self.log_filename, backupCount=5)
        )
        if os.path.exists(self.log_filename):
            # rollover upon every startup, not based on file size.  most recent
            # is log_filename, previous is log_filename+".1", and so on.
            root_logger.handlers[0].doRollover()

    def run(self):
        self.setup_logging()

        signal.signal(signal.SIGCHLD, wait_signal_handler)
        signal.signal(signal.SIGTERM, lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGINT,  lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGPIPE, lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGUSR1, lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGUSR2, lambda signum, frame: self.ticker.stop())

        self.wm.manage()
        self.ticker.tick_forever()

