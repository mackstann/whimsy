# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, XK

class binding_base(object):
    def __init__(self, detail, mods, passthrough=False):
        self.detail = detail
        self.mods = mods
        self.passthrough = passthrough

    def __call__(self, ev, **kw):
        if self._should_at_least_be_swallowed(ev):
            if not self.passthrough:
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

    def __init__(self, keyname, mods, **kw):
        self.keyname = keyname
        binding_base.__init__(self, None, mods, **kw)

    def __call__(self, wm, **kw):
        if self.detail is None:
            # maybe we should just do this in __init__
            self.detail = wm.dpy.keysym_to_keycode(
                XK.string_to_keysym(self.keyname)
            )
        return binding_base.__call__(self, wm=wm, **kw)

class if_key_release(if_key_press):
    execute_event_types = [X.KeyRelease]
    swallow_event_types = [X.KeyRelease]

class if_button_press(binding_base):
    execute_event_types = [X.ButtonPress]
    swallow_event_types = [X.ButtonPress, X.ButtonRelease]

class if_button_release(if_button_press):
    execute_event_types = [X.ButtonRelease]
    swallow_event_types = [X.ButtonRelease]

