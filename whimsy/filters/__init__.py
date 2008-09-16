# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xutil
from Xlib import error as Xerror

from whimsy import util

class if_event_type(object):
    'true if the event type is one of *evtypes'
    def __init__(self, *evtypes):
        self.evtypes = evtypes
    def __call__(self, ev, **kw):
        return ev.type in self.evtypes

def if_client(wm, ev, **kw):
    'true if the window is an application window managed by the window manager'
    return 'win' in kw and util.window_type(wm, kw['win']) == 'client'

def if_root(wm, ev, **kw):
    'true if the window is the root window (desktop/background)'
    return 'win' in kw and util.window_type(wm, kw['win']) == 'root'

def if_unmanaged(wm, win, ev, **kw):
    return (
        hasattr(ev, 'window') and
        util.window_type(wm, win) == 'unmanaged'
    )

class if_state(object):
    'true if modifier (shift/control/etc) keys currently match mods'
    def __init__(self, mods):
        self.mods = mods
    def __call__(self, ev, **kw):
        return self.mods.matches(ev.state)

class if_(object):
    'convenience class for filtering by event type and/or window type'
    def __init__(self, evtype, wintype=None):
        self.evtype = evtype
        self.wintype = wintype
    def __call__(self, wm, ev, **kw):
        if ev.type != self.evtype or 'win' not in kw:
            return False
        if self.wintype is None:
            return True
        return util.window_type(wm, kw['win']) == self.wintype

# TODO: move these into window_manager, minus the if_; keep if_ versions here
# as wrapper filters
def if_should_manage_existing_window(win, **kw):
    attr = win.get_attributes()
    return (
        not attr.override_redirect
        and attr.map_state == X.IsViewable
        and getattr(win.get_wm_hints(), 'initial_state', not Xutil.NormalState)
            == Xutil.NormalState
    )

def if_should_manage_new_window(win, **kw):
    catch = Xerror.CatchError(Xerror.BadWindow)
    return not win.get_attributes().override_redirect and not catch.get_error()


