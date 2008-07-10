# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, signal, logging, logging.handlers
from Xlib import display
from whimsy import infrastructure, signals
from whimsy.window_manager import window_manager
from whimsy.controllers.x_event_controller import x_event_controller
from whimsy.controllers.tick_controller import tick_controller

class main(object):
    def __init__(self):
        infrastructure.set_display_env()

        self.dpy    = dpy    = display.Display()
        self.hub    = hub    = signals.publisher()
        self.wm     = wm     = window_manager(hub, dpy)
        self.xec    = xec    = x_event_controller(hub, dpy)
        self.ticker = ticker = tick_controller(hub)

        self.hub.defaults['wm'] = wm
        self.hub.defaults['hub'] = hub

        # if a tick hasn't happened for 10 seconds we've definitely gotten stuck
        self.hub.register('tick', lambda s: signal.alarm(10))
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
            root_logger.handlers[0].doRollover()

    def run(self):
        self.setup_logging()

        signal.signal(signal.SIGCHLD, infrastructure.wait_signal_handler)
        signal.signal(signal.SIGTERM, lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGINT,  lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGPIPE, lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGUSR1, lambda signum, frame: self.ticker.stop())
        signal.signal(signal.SIGUSR2, lambda signum, frame: self.ticker.stop())

        self.wm.manage()
        self.ticker.tick_forever()

