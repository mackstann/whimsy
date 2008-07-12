# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

class transformation(object):
    def __init__(self, client, initial_pointer_x, initial_pointer_y):
        self.client = client
        self.initial_pointer_x = initial_pointer_x
        self.initial_pointer_y = initial_pointer_y
        self.initial_client_x = client.geom['x']
        self.initial_client_y = client.geom['y']
        self.initial_client_width = client.geom['width']
        self.initial_client_height = client.geom['height']

class interactive_pointer_transformer(object):
    state = None

    def __call__(self, signal):
        self.grab(signal)
        #signal.hub.push_context()
        signal.hub.register('motion_notify', self.motion)
        signal.hub.register('button_release', self.ungrab)

    def grab(self, signal):
        client = signal.wm.window_to_client(signal.win)
        self.state = transformation(client, signal.ev.root_x, signal.ev.root_y)
        client.win.grab_pointer(True,
            X.PointerMotionMask | X.ButtonReleaseMask,
            X.GrabModeAsync, X.GrabModeAsync, X.NONE,
            X.NONE, # why doesn't Xcursorfont.left_ptr work for pointer?
            X.CurrentTime
        )

    def motion(self, signal):
        # if we had XCheckTypedWindowEvent we could compress motionnotifies here
        xdelta = signal.ev.root_x - self.state.initial_pointer_x
        ydelta = signal.ev.root_y - self.state.initial_pointer_y
        self.transform(xdelta, ydelta)

    def ungrab(self, signal):
        signal.wm.dpy.ungrab_pointer(X.CurrentTime)
        signal.hub.unregister(self.motion)
        signal.hub.unregister(self.ungrab)
        self.state = None

    def transform(self, xdelta, ydelta):
        raise NotImplementedError

class move_transformer(interactive_pointer_transformer):
    def transform(self, xdelta, ydelta):
        self.state.client.moveresize(
            x = self.state.initial_client_x + xdelta,
            y = self.state.initial_client_y + ydelta
        )

class resize_transformer(interactive_pointer_transformer):
    def transform(self, xdelta, ydelta):
        self.state.client.moveresize(
            width = self.state.initial_client_width + xdelta,
            height = self.state.initial_client_height + ydelta
        )

