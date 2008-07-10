# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

def replay_or_swallow(dpy, ev, replay):
    what = ev.__class__.__name__.startswith("Key") and "Keyboard" or "Pointer"
    how = replay and "Replay" or "Async"

    # beware, voodoo!  this is pretty much the only correct way to do this
    # without letting events leak through or other bad stuff
    dpy.allow_events(getattr(X, how+what), ev.time)
    if replay:
        dpy.flush()

