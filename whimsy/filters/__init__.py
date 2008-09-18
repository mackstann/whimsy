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

def _if_win_type(wtype, wm, ev, **kw):
    return 'win' in kw and util.window_type(wm, kw['win']) == wtype

def if_client   (wm, ev, **kw): return _if_win_type('client',    wm, ev, **kw)
def if_root     (wm, ev, **kw): return _if_win_type('root',      wm, ev, **kw)
def if_unmanaged(wm, ev, **kw): return _if_win_type('unmanaged', wm, ev, **kw)

class if_state(object):
    'true if modifier (shift/control/etc) keys currently match mods'
    def __init__(self, mods):
        self.mods = mods
    def __call__(self, ev, **kw):
        return self.mods.matches(ev.state)

class if_state_not(if_state):
    def __call__(self, ev, **kw):
        return not super(if_state_not, self).__call__(ev, **kw)

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
    try:
        return not win.get_attributes().override_redirect
    except Xerror.BadWindow:
        # it disappeared
        return False


