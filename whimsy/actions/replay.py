# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.x11.replay import replay

class smart_replay(object):
    def __init__(self):
        self.swallow = False

    def mark_current_event_for_swallowing(self, **kw):
        self.swallow = True

    def __call__(self, wm, ev, **kw):
        replay(wm.dpy, ev, not self.swallow)
        self.swallow = False

