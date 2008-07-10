# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xutil
from Xlib import error as Xerror

from whimsy import util

class if_event_type(object):
    def __init__(self, *evtypes):
        self.evtypes = evtypes
    def __call__(self, signal):
        return signal.ev.type in self.evtypes

def if_client(signal):
    return (
        hasattr(signal.ev, 'window') and
        util.window_type(signal.wm, signal.win) == 'client'
    )

def if_root(signal):
    return (
        hasattr(signal.ev, 'window') and
        util.window_type(signal.wm, signal.win) == 'root'
    )

class if_state(object):
    def __init__(self, mods):
        self.mods = mods
    def __call__(self, signal):
        return self.mods.matches(signal.ev.state)

class if_(object):
    def __init__(self, evtype, wintype=None):
        self.evtype = evtype
        self.wintype = wintype
    def __call__(self, signal):
        if signal.ev.type != self.evtype:
            return False
        if self.wintype is None:
            return True
        return util.window_type(signal.wm, signal.win) == self.wintype

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
        def filt(signal):
            return self.count == desired_count
        return filt

    def __call__(self, signal):
        """should be called on every button press event, to keep track of fast
        successive clicks"""

        try:
            prev = self.prev_click
        except:
            is_repeat = False
        else:
            is_repeat = (
                signal.ev.window.id == prev.window.id and
                signal.ev.detail == prev.detail and
                signal.ev.state == prev.state and
                (signal.ev.time - prev.time) <= self.timeout_ms and
                abs(signal.ev.root_x - prev.root_x) <= self.pixel_distance and
                abs(signal.ev.root_y - prev.root_y) <= self.pixel_distance
            )

        if is_repeat:
            self.count += 1
        else:
            self.count = 1

        self.prev_click = signal.ev

# move these into window_manager, minus the if_; keep if_ versions here as
# wrapper filters
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
    return not signal.win.get_attributes().override_redirect and not catch.get_error()


