# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X
import time

def replay(dpy, ev, replay_or_not):
    what = "Keyboard" if ev.__class__.__name__[0] == "K" else "Pointer"
    how = "Replay" if replay_or_not else "Async"

    print "%.3f"%time.time(), ev.time, how+what, ev.__class__.__name__
    dpy.allow_events(getattr(X, how+what), ev.time)
    dpy.flush()

