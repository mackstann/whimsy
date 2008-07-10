# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy import signals

class interactive_pointer_transform(object):
    def __init__(self, dpy, client, begin_event):
        self.dpy = dpy
        self.client = client
        self.begin_event = begin_event
        self.begin_geom = client.geom.copy()
        self.client.win.grab_pointer(True,
            X.PointerMotionMask | X.ButtonReleaseMask,
            X.GrabModeAsync, X.GrabModeAsync, X.NONE,
            X.NONE, # why doesn't Xcursorfont.left_ptr work for pointer?
            X.CurrentTime
        )

    def __call__(self, signal):
        ev = signal.ev

        if ev.__class__.__name__ == "MotionNotify":
            # if we had XCheckTypedWindowEvent we could compress motionnotifies
            # here

            xdelta = ev.root_x - self.begin_event.root_x
            ydelta = ev.root_y - self.begin_event.root_y
            self._update(xdelta, ydelta)

        elif ev.__class__.__name__ == "ButtonRelease":
            self.dpy.ungrab_pointer(X.CurrentTime)
            signal.hub.unregister(self)

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

class start_move(object):
    def __call__(self, signal):
        signal.hub.register('event_begin',
            move_transformer(
                signal.wm.dpy,
                signal.wm.window_to_client(signal.win),
                signal.ev
            )
        )

class start_resize(object):
    def __call__(self, signal):
        signal.hub.register('event_begin',
            resize_transformer(
                signal.wm.dpy,
                signal.wm.window_to_client(signal.win),
                signal.ev
            )
        )

