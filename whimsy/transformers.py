# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from Xlib import X

from whimsy.log import *
from whimsy import event, util, signals

class interactive_pointer_transform:
    def __init__(self, client, begin_event):
        self.client = client
        self.begin_event = begin_event
        self.begin_geom = client.geom.copy()
        self.client.win.grab_pointer(True,
            X.PointerMotionMask | X.ButtonReleaseMask |
            X.EnterWindowMask | X.LeaveWindowMask,
            X.GrabModeAsync, X.GrabModeAsync, X.NONE,
            X.NONE, # why doesn't Xcursorfont.left_ptr work for pointer?
            X.CurrentTime
        )

    def __del__(self):
        debug('transformer deleted')

    def __call__(self, signal):
        ev = signal.ev
        assert not hasattr(self, 'deleted')

        if ev.__class__.__name__ == "MotionNotify":
            ev = event.check_typed_window_event(signal.wm.dpy, ev, type=X.MotionNotify, window=self.client.win)

            xdelta = ev.root_x - self.begin_event.root_x
            ydelta = ev.root_y - self.begin_event.root_y
            self._update(xdelta, ydelta)

        elif ev.__class__.__name__ == "ButtonRelease":
            self.client.wm.dpy.ungrab_pointer(X.CurrentTime)
            self.deleted = True
            return signals.return_code.DELETE_HANDLER

        elif ev.__class__.__name__ == "EnterNotify":
            return signals.return_code.SIGNAL_FINISHED
        elif ev.__class__.__name__ == "LeaveNotify":
            return signals.return_code.SIGNAL_FINISHED

    def _update(self, xdelta, ydelta):
        raise NotImplementedError

class move_transformer(interactive_pointer_transform):
    def _update(self, xdelta, ydelta):
        self.client.moveresize(
            x = self.begin_geom['x'] + xdelta,
            y = self.begin_geom['y'] + ydelta
        )

class resize_transformer(interactive_pointer_transform):
    def _update(self, xdelta, ydelta):
        self.client.moveresize(
            width = self.begin_geom['width'] + xdelta,
            height = self.begin_geom['height'] + ydelta
        )

