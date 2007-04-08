# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from Xlib import X
from Xlib.protocol import rq

from whimsy.log import *

class click_memory(object):
    """     
    remembers details about the last click to determine double clicks, triple
    clicks, etc.  pass it every button press, and then query the .count member
    to determine how many clicks have occurred in quick succession.
    """

    multiclick_pixel_distance = 15
    multiclick_timeout_ms = 400

    ev = None

    @classmethod
    def is_repeated_click(cls, prev, ev):
        return (
            prev != None and
            ev.window == prev.window and
            ev.detail == prev.detail and
            (ev.time - prev.time) <= cls.multiclick_timeout_ms and
            abs(ev.root_x - prev.root_x) <= cls.multiclick_pixel_distance and
            abs(ev.root_y - prev.root_y) <= cls.multiclick_pixel_distance
        )

    def remember(self, ev):
        if ev.__class__.__name__ == "ButtonPress":
            if not self.is_repeated_click(self.ev, ev):
                self.count = 0
            self.count += 1
            self.ev = ev

def replay_or_swallow(dpy, ev, replay):
    if ev.type not in (X.ButtonPress, X.ButtonRelease, X.KeyPress, X.KeyRelease):
        return

    what = ev.__class__.__name__.startswith("Key") and "Keyboard" or "Pointer"
    how = replay and "Replay" or "Async"

    # beware, voodoo!  this is pretty much the only correct way to do this
    # without letting events leak through or other bad stuff
    dpy.allow_events(getattr(X, how+what), ev.time)
    if replay:
        dpy.flush()

class smart_replay:
    def __call__(self, signal):
        if not hasattr(signal.ev, 'already_replayed'):
            replay_or_swallow(signal.wm.dpy, signal.ev, not hasattr(signal.ev, 'swallow'))
            signal.ev.already_replayed = True

def check_typed_window_event(dpy, start_event, type=None, window=None):
    last_good = start_event
    while dpy.pending_events():
        e = dpy.next_event(type=type, window=window)
        if not e:
            return last_good
        last_good = e
    last_good.wm = start_event.wm
    return last_good

