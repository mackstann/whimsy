# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

class transformation(object):
    def __init__(self, client, button, initial_pointer_x, initial_pointer_y):
        self.client = client
        self.button = button
        self.initial_pointer_x = initial_pointer_x
        self.initial_pointer_y = initial_pointer_y
        self.initial_client_geom = client.geom.move(0,0)

class interactive_pointer_transformer(object):
    state = None

    def __call__(self, hub, **kw):
        self.grab(hub=hub, **kw)
        #hub.push_context()
        hub.attach('motion_notify', self.motion)
        hub.attach('button_release', self.maybe_ungrab)

    def grab(self, wm, win, ev, **kw):
        client = wm.find_client(win)
        self.state = transformation(client, ev.detail, ev.root_x, ev.root_y)
        client.win.grab_pointer(True,
            X.PointerMotionMask | X.ButtonPressMask | X.ButtonReleaseMask,
            X.GrabModeAsync, X.GrabModeAsync, X.NONE,
            X.NONE, # why doesn't Xcursorfont.left_ptr work for pointer?
            X.CurrentTime
        )

    def motion(self, ev, **kw):
        # if we had XCheckTypedWindowEvent we could compress motionnotifies here
        xdelta = ev.root_x - self.state.initial_pointer_x
        ydelta = ev.root_y - self.state.initial_pointer_y
        self.transform(xdelta, ydelta)
        self.state.client.moveresize()

    def maybe_ungrab(self, hub, wm, ev, **kw):
        if ev.detail != self.state.button:
            return
        wm.dpy.ungrab_pointer(X.CurrentTime)
        hub.detach(self.motion)
        hub.detach(self.maybe_ungrab)
        self.state = None

    def transform(self, xdelta, ydelta):
        raise NotImplementedError

class start_move(interactive_pointer_transformer):
    def transform(self, xdelta, ydelta):
        self.state.client.geom = self.state.initial_client_geom.move(xdelta, ydelta)

class start_resize(interactive_pointer_transformer):
    def transform(self, xdelta, ydelta):
        self.state.client.geom.size = \
            self.state.initial_client_geom.inflate(xdelta, ydelta).size

