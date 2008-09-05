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

    def __call__(self, hub, **kw):
        self.grab(hub=hub, **kw)
        #hub.push_context()
        hub.register('motion_notify', self.motion)
        hub.register('button_release', self.ungrab)

    def grab(self, wm, win, ev, **kw):
        client = wm.find_client(win)
        self.state = transformation(client, ev.root_x, ev.root_y)
        client.win.grab_pointer(True,
            X.PointerMotionMask | X.ButtonReleaseMask,
            X.GrabModeAsync, X.GrabModeAsync, X.NONE,
            X.NONE, # why doesn't Xcursorfont.left_ptr work for pointer?
            X.CurrentTime
        )

    def motion(self, ev, **kw):
        # if we had XCheckTypedWindowEvent we could compress motionnotifies here
        xdelta = ev.root_x - self.state.initial_pointer_x
        ydelta = ev.root_y - self.state.initial_pointer_y
        self.transform(xdelta, ydelta)

    def ungrab(self, hub, wm, **kw):
        wm.dpy.ungrab_pointer(X.CurrentTime)
        hub.unregister(self.motion)
        hub.unregister(self.ungrab)
        self.state = None

    def transform(self, xdelta, ydelta):
        raise NotImplementedError

class start_move(interactive_pointer_transformer):
    def transform(self, xdelta, ydelta):
        self.state.client.moveresize(
            x = self.state.initial_client_x + xdelta,
            y = self.state.initial_client_y + ydelta
        )

class start_resize(interactive_pointer_transformer):
    def transform(self, xdelta, ydelta):
        self.state.client.moveresize(
            width = self.state.initial_client_width + xdelta,
            height = self.state.initial_client_height + ydelta
        )

