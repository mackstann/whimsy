# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, XK

class binding_base(object):
    def __init__(self, detail, mods):
        self.detail = detail
        self.mods = mods

    def __call__(self, hub, ev, **kw):
        return (
            # type must be first because the attributes of ev depend on it
            ev.type == self.event_type and
            self.detail == ev.detail and
            self.mods.matches(ev.state)
        )

class if_key_press(binding_base):
    event_type = X.KeyPress

    def __connected__(self, wm, **kw):
        # for convenience, what we initially get passed is a string of a key
        # name; convert that to a real keycode before anyone tries to call us
        self.detail = wm.dpy.keysym_to_keycode(
            XK.string_to_keysym(self.detail))

class if_button_press(binding_base):
    event_type = X.ButtonPress

