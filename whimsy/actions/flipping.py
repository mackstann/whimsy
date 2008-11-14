# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import time as _time

from whimsy.actions import transformers as _transformers
from whimsy.actions.builtins import viewport_relative_move as _view_rel_mv

class _flipper(object):
    # so an edge flip doesn't trigger another opposite edge flip, and so on
    # continuously, we warp the pointer from, say, the rightmost pixel, to the
    # leftmost pixel PLUS this margin
    safety_margin = 10

    # and for hectic situations, impose a minimum time interval between flips
    time_margin = 0.1

    last_flip = 0

    def maybe_flip(self, hub, wm, ev, **kw):
        if _time.time() - self.last_flip < self.time_margin:
            return

        if not hasattr(self, 'root_geometry'):
            self.root_geometry = wm.root.get_geometry()

        width = self.root_geometry.width
        height = self.root_geometry.height

        vert_warp = height - self.safety_margin
        horiz_warp = width - self.safety_margin

        if ev.root_x == width-1:
            warp_by     = (-horiz_warp, 0)
            viewport_by = (+width, 0)
            client_by   = (+self.safety_margin, 0)
        elif ev.root_y == height-1:
            warp_by     = (0, -vert_warp)
            viewport_by = (0, +height)
            client_by   = (0, +self.safety_margin)
        elif ev.root_x == 0:
            warp_by     = (+horiz_warp, 0)
            viewport_by = (-width, 0)
            client_by   = (-self.safety_margin, 0)
        elif ev.root_y == 0:
            warp_by     = (0, +vert_warp)
            viewport_by = (0, -height)
            client_by   = (0, -self.safety_margin)
        else:
            return

        if not wm.can_move_viewport_by(*viewport_by):
            return

        self.flip(hub, wm, warp_by, viewport_by, client_by)

    def flip(self, hub, wm, warp_by, viewport_by, client_by):
        wm.dpy.grab_server()
        self.state.client.dpy.warp_pointer(*warp_by)
        _view_rel_mv(*viewport_by)(hub=hub, wm=wm)
        self.client_adjust(warp_by, viewport_by, client_by)
        wm.dpy.sync()
        wm.dpy.ungrab_server()
        self.last_flip = _time.time()

    def client_adjust(self):
        raise NotImplementedError

class flipping_move(_transformers.start_move, _flipper):
    def client_adjust(self, warp_by, viewport_by, client_by):
        self.state.client.moveresize_rel(
            x=client_by[0],
            y=client_by[1],
        )

    def motion(self, **kw):
        super(flipping_move, self).motion(**kw)
        self.maybe_flip(**kw)

class flipping_resize(_transformers.start_resize, _flipper):
    def client_adjust(self, warp_by, viewport_by, client_by):
        self.state.initial_pointer_x -= viewport_by[0]
        self.state.initial_pointer_y -= viewport_by[1]
        self.state.client.moveresize_rel(
            width=client_by[0],
            height=client_by[1],
        )

    def motion(self, **kw):
        super(flipping_resize, self).motion(**kw)
        self.maybe_flip(**kw)


