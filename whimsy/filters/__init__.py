# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xutil
from Xlib import error as Xerror

from whimsy import util
from whimsy.models.client import existing_unmanaged_window, newly_mapped_window

class if_event_type(object):
    'true if the event type is one of *evtypes'
    def __init__(self, *evtypes):
        self.evtypes = evtypes
    def __call__(self, ev, **kw):
        return ev.type in self.evtypes

def _if_win_type(wtype, wm, **kw):
    return 'win' in kw and util.window_type(wm, kw['win']) == wtype

def if_client   (wm, **kw): return _if_win_type('client',    wm, **kw)
def if_root     (wm, **kw): return _if_win_type('root',      wm, **kw)
def if_unmanaged(wm, **kw): return _if_win_type('unmanaged', wm, **kw)

class if_state(object):
    'true if modifier (shift/control/etc) keys currently match mods'
    def __init__(self, mods):
        self.mods = mods
    def __call__(self, ev, **kw):
        return self.mods.matches(ev.state)

class if_state_not(if_state):
    def __call__(self, ev, **kw):
        return not if_state.__call__(self, ev, **kw)

def if_should_manage_existing_window(win, **kw):
    return existing_unmanaged_window(win).should_manage()

def if_should_manage_new_window(win, **kw):
    return newly_mapped_window(win).should_manage()


