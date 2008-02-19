# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xutil
from Xlib import error as Xerror

from whimsy import util, props

class if_event_type:
    def __init__(self, *evtypes):
        self.evtypes = evtypes
    def __call__(self, signal):
        return signal.ev.type in self.evtypes

def if_client(signal):
    return (
        hasattr(signal.ev, 'window') and
        util.window_type(signal.wm, signal.ev.window) == 'client'
    )

def if_root(signal):
    return (
        hasattr(signal.ev, 'window') and
        util.window_type(signal.wm, signal.ev.window) == 'root'
    )

class if_state:
    def __init__(self, mods):
        self.mods = mods
    def __call__(self, signal):
        return self.mods.matches(signal.ev.state)

class if_:
    def __init__(self, evtype, wintype=None):
        self.evtype = evtype
        self.wintype = wintype
    def __call__(self, signal):
        if signal.ev.type != self.evtype:
            return False
        if self.wintype is None:
            return True
        return util.window_type(signal.wm, signal.ev.window) == self.wintype

class if_multiclick:
    def __init__(self, count):
        self.count = count
    def __call__(self, signal):
        return self.count == \
            props.get_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_MULTICLICK_COUNT')

def if_should_manage_existing_window(signal):
    attr = signal.win.get_attributes()
    return (
        not attr.override_redirect
        and attr.map_state == X.IsViewable
        and getattr(signal.win.get_wm_hints(), 'initial_state', not Xutil.NormalState)
        == Xutil.NormalState
    )

def if_should_manage_new_window(signal):
    catch = Xerror.CatchError(Xerror.BadWindow)
    return not signal.ev.window.get_attributes().override_redirect and not catch.get_error()


