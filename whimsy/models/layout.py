# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.x11 import props, size_hints

class layout(object):

    def __init__(self, hub, wm):
        self.hub = hub
        self.wm = wm
        self.sizehints = {}
        hub.attach('after_manage_window', self.add_client)
        hub.attach('after_unmanage_window', self.remove_client)
        hub.attach('before_moveresize_client', self.constrain_moveresize)

    def add_client(self, client, **kw):
        self.sizehints[client.win.id] = size_hints.size_hints(win=client.win)

    def remove_client(self, hub, wm, win, **kw):
        if win.id in self.sizehints:
            del self.sizehints[win.id]

    def constrain_moveresize(self, client, **kw):
        sh = self.sizehints[client.win.id]
        w, h = client.geom.size
        w, h = sh.fix_min(w, h)
        w, h = sh.fix_max(w, h)
        w, h = sh.fix_increments(w, h)
        w, h = sh.fix_aspect(w, h)
        client.geom.size = w, h

