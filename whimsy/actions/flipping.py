# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.actions import transformers
from whimsy.actions.builtins import viewport_relative_move

class flipping_transformer(transformers.interactive_pointer_transformer):
    def __call__(self, signal):
        super(flipping_transformer, self).__call__(signal)
        self.root_geometry = signal.wm.root.get_geometry()

    def motion(self, signal):
        super(flipping_transformer, self).motion(signal)
        ev = signal.ev
        warp_pointer = signal.wm.dpy.warp_pointer
        width = self.root_geometry.width
        height = self.root_geometry.height
        safety_margin = 10
        vert_warp = height - safety_margin
        horiz_warp = width - safety_margin
        left = 0
        right = width - 1
        top = 0
        bottom = height - 1
        print (ev.root_x, ev.root_y)
        if ev.root_x == right:
            warp_by     = (-horiz_warp, 0)
            viewport_by = (+width, 0)
            client_by   = (+safety_margin, 0)
        elif ev.root_y == bottom:
            warp_by     = (0, -vert_warp)
            viewport_by = (0, +height)
            client_by   = (0, +safety_margin)
        elif ev.root_x == left:
            warp_by     = (+horiz_warp, 0)
            viewport_by = (-width, 0)
            client_by   = (-safety_margin, 0)
        elif ev.root_y == top:
            warp_by     = (0, +vert_warp)
            viewport_by = (0, -height)
            client_by   = (0, -safety_margin)
        else:
            return

        print "warp_by:", warp_by
        print "viewport_relative_move by:", viewport_by
        warp_pointer(*warp_by)
        viewport_relative_move(*viewport_by)(signal)
        self.state.client.moveresize_rel(x=client_by[0], y=client_by[1])
        signal.wm.dpy.sync()

class flipping_move(transformers.move_transformer, flipping_transformer):
    pass

class flipping_resize(transformers.resize_transformer, flipping_transformer):
    pass
