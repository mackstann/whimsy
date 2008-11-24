# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xutil
from Xlib import error as Xerror

from whimsy import util
from whimsy.x11 import props
from whimsy.models.client import existing_unmanaged_window, newly_mapped_window

class if_event_type(object):
    'true if the event type is one of *evtypes'
    def __init__(self, *evtypes):
        self.evtypes = evtypes
    def __call__(self, ev, **kw):
        return ev.type in self.evtypes

def _if_win_type(wtype, wm, **kw):
    return 'win' in kw and util.window_type(wm, kw['win']) == wtype

def if_client   (**kw): return _if_win_type('client',    **kw)
def if_root     (**kw): return _if_win_type('root',      **kw)
def if_unmanaged(**kw): return _if_win_type('unmanaged', **kw)

def _if_hinted_win_type(wtypes, wm, **kw):
    if 'win' not in kw:
        return False
    types = set(props.get_prop(wm.dpy, kw['win'], '_NET_WM_WINDOW_TYPE'))
    ours = set([
        wm.dpy.get_atom('_NET_WM_WINDOW_TYPE_'+wtype.upper())
        for wtype in wtypes
    ])
    return bool(ours & types)

def if_desktop_type(**kw): return _if_hinted_win_type(['desktop'], **kw)
def if_dock_type   (**kw): return _if_hinted_win_type(['dock'   ], **kw)
def if_toolbar_type(**kw): return _if_hinted_win_type(['toolbar'], **kw)
def if_menu_type   (**kw): return _if_hinted_win_type(['menu'   ], **kw)
def if_utility_type(**kw): return _if_hinted_win_type(['utility'], **kw)
def if_splash_type (**kw): return _if_hinted_win_type(['splash' ], **kw)
def if_dialog_type (**kw): return _if_hinted_win_type(['dialog' ], **kw)
def if_normal_type (**kw): return _if_hinted_win_type(['normal' ], **kw)

def _if_hinted_win_state(wstates, wm, **kw):
    if 'win' not in kw:
        return False
    states = set(props.get_prop(wm.dpy, kw['win'], '_NET_WM_STATE'))
    ours = set([
        wm.dpy.get_atom('_NET_WM_STATE_'+wstate.upper())
        for wstate in wstates
    ])
    return bool(ours & states)

def if_modal            (**kw): return _if_hinted_win_state(['modal'            ], **kw)
def if_sticky           (**kw): return _if_hinted_win_state(['sticky'           ], **kw)
def if_maximized_vert   (**kw): return _if_hinted_win_state(['maximized_vert'   ], **kw)
def if_maximized_horz   (**kw): return _if_hinted_win_state(['maximized_horz'   ], **kw)
def if_shaded           (**kw): return _if_hinted_win_state(['shaded'           ], **kw)
def if_skip_taskbar     (**kw): return _if_hinted_win_state(['skip_taskbar'     ], **kw)
def if_skip_pager       (**kw): return _if_hinted_win_state(['skip_pager'       ], **kw)
def if_hidden           (**kw): return _if_hinted_win_state(['hidden'           ], **kw)
def if_fullscreen       (**kw): return _if_hinted_win_state(['fullscreen'       ], **kw)
def if_above            (**kw): return _if_hinted_win_state(['above'            ], **kw)
def if_below            (**kw): return _if_hinted_win_state(['below'            ], **kw)
def if_demands_attention(**kw): return _if_hinted_win_state(['demands_attention'], **kw)

def if_manipulable(**kw):
    return _if_win_type('client', **kw) and \
       not _if_hinted_win_type(['desktop', 'dock', 'splash'], **kw)

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


