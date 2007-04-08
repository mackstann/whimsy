# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from Xlib import X, XK

from whimsy import event

from whimsy.log import *

# instead of registering the replayer to the main event signal, we should
# register it to the event's done_processing signal (...?)

class binding_base:
    def __init__(self, detail, mods, **options):
        self.detail = detail
        self.mods = mods
        self.options = options

    def __call__(self, signal):
        ev = signal.ev
        if self._should_at_least_be_swallowed(ev):
            if not self.options.get('passthru', False):
                ev.swallow = True
            return self._should_be_executed(ev)

    def _should_at_least_be_swallowed(self, ev):
        return (
            ev.type in self.swallow_event_types and
            self.detail == ev.detail and
            self.mods.matches(ev.state)
        )
                                                                                                           
    def _should_be_executed(self, ev):
        return ev.type in self.execute_event_types

class if_key_press(binding_base):
    execute_event_types = [X.KeyPress]
    swallow_event_types = [X.KeyPress, X.KeyRelease]

    def __init__(self, keyname, mods, **options):
        self.keyname = keyname
        binding_base.__init__(self, None, mods, **options)

    def __call__(self, signal):
        if self.detail == None:
            self.detail = signal.wm.dpy.keysym_to_keycode(
                XK.string_to_keysym(self.keyname)
            )
        return binding_base.__call__(self, signal)

class if_button_press(binding_base):
    execute_event_types = [X.ButtonPress]
    swallow_event_types = [X.ButtonPress, X.ButtonRelease]

class if_button_release(if_button_press):
    execute_event_types = [X.ButtonRelease]
    swallow_event_types = [X.ButtonRelease]

class if_key_release(if_key_press):
    execute_event_types = [X.KeyRelease]
    swallow_event_types = [X.KeyRelease]

