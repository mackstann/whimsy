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

class click_counter(object):
    """built like an action but yields a filter which is its main purpose -- to
    filter for double clicks, triple clicks, etc"""

    def __init__(self, pixel_distance=15, timeout_ms=400):
        self.pixel_distance = pixel_distance
        self.timeout_ms = timeout_ms
        self.count = 0

    def if_multi(self, desired_count):
        """returns a filter that will tell you whether the current click is a
        double click or triple click or whatever you specify"""
        def filt(**kw):
            return self.count == desired_count
        return filt

    def __call__(self, ev, **kw):
        """should be called on every button press event, to keep track of fast
        successive clicks"""

        try:
            prev = self.prev_click
        except:
            is_repeat = False
        else:
            is_repeat = (
                ev.window.id == prev.window.id and
                ev.detail == prev.detail and
                ev.state == prev.state and
                (ev.time - prev.time) <= self.timeout_ms and
                abs(ev.root_x - prev.root_x) <= self.pixel_distance and
                abs(ev.root_y - prev.root_y) <= self.pixel_distance
            )

        if is_repeat:
            self.count += 1
        else:
            self.count = 1

        self.prev_click = ev

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


