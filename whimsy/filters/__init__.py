# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from Xlib import X

from whimsy import util, props

class if_event_type:
    def __init__(self, *evtypes):
        self.evtypes = evtypes
    def __call__(self, signal):
        return signal.ev.type in self.evtypes

def if_client(signal):
    return util.window_type(signal.wm, signal.ev.window) == 'client'

def if_root(signal):
    return util.window_type(signal.wm, signal.ev.window) == 'root'

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

