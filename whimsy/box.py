# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import from Xlib.protocol.request import GetGeometry

class box(object):
    def __init__(self, *a, **kw):
        if len(a) == 1 and len(kw) == 0:
            if isinstance(a[0], GetGeometry):
                self.init_from_geometry_obj(a[0])

    def init_from_geometry_obj(self, geom):
        self.x = geom.x
        self.y = geom.y
        self.width = geom.width
        self.height = geom.height

    def _get_right(self):
        return self.x + self.width - 1
    def _get_bottom(self):
        return self.y + self.height - 1

    def _set_right(self, val):
        self.width = val - self.x + 1
    def _set_bottom(self, val):
        self.height = val - self.y + 1

    right = property(_get_right, _set_right)
    bottom = property(_get_bottom, _set_bottom)

# XXX abandoned in favor of pygame Rect.  saved just in case

#GetGeometry
#<Xlib.protocol.request.GetGeometry serial = 8, data = {'height': 1200, 'width': 1920, 'depth': 24, 'y': 0, 'x': 0, 'border_width': 0, 'root': <Xlib.display.Window 0x0000005f>, 'sequence_number': 8}, error = None>

