# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.actions import transformers
from whimsy.actions.builtins import viewport_relative_move

class flipping_transformer(transformers.interactive_pointer_transformer):
    # so an edge flip doesn't trigger another opposite edge flip, and so on
    # continuously, we warp the pointer from, say, the rightmost pixel, to the
    # leftmost pixel PLUS this margin
    safety_margin = 10

    def __call__(self, wm, **kw):
        super(flipping_transformer, self).__call__(wm=wm, **kw)
        self.root_geometry = wm.root.get_geometry()

    def motion(self, wm, ev, **kw):
        super(flipping_transformer, self).motion(wm=wm, ev=ev, **kw)
        width = self.root_geometry.width
        height = self.root_geometry.height

        vert_warp = height - self.safety_margin
        horiz_warp = width - self.safety_margin

        left = 0
        top = 0
        right = width - 1
        bottom = height - 1

        if ev.root_x == right:
            self.warp_by     = (-horiz_warp, 0)
            self.viewport_by = (+width, 0)
            self.client_by   = (+self.safety_margin, 0)
        elif ev.root_y == bottom:
            self.warp_by     = (0, -vert_warp)
            self.viewport_by = (0, +height)
            self.client_by   = (0, +self.safety_margin)
        elif ev.root_x == left:
            self.warp_by     = (+horiz_warp, 0)
            self.viewport_by = (-width, 0)
            self.client_by   = (-self.safety_margin, 0)
        elif ev.root_y == top:
            self.warp_by     = (0, +vert_warp)
            self.viewport_by = (0, -height)
            self.client_by   = (0, -self.safety_margin)
        else:
            return

        if not wm.can_move_viewport_by(*self.viewport_by):
            return

        self.warp(wm=wm, **kw)

        del self.warp_by
        del self.viewport_by
        del self.client_by

    def warp(self, wm, **kw):
        self.state.client.dpy.warp_pointer(*self.warp_by)
        viewport_relative_move(*self.viewport_by)(wm=wm, **kw)
        self.client_adjust()
        wm.dpy.sync()

    def client_adjust(self):
        raise NotImplementedError

class flipping_move(transformers.move_transformer, flipping_transformer):
    def client_adjust(self):
        self.state.client.moveresize_rel(
            x=self.client_by[0],
            y=self.client_by[1],
        )

class flipping_resize(transformers.resize_transformer, flipping_transformer):
    def client_adjust(self):
        self.state.initial_pointer_x -= self.viewport_by[0]
        self.state.initial_pointer_y -= self.viewport_by[1]
        self.state.client.moveresize_rel(
            width=self.client_by[0],
            height=self.client_by[1],
        )

