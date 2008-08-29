# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, XK

class binding_base(object):
    def __init__(self, detail, mods):
        self.detail = detail
        self.mods = mods

    def __call__(self, hub, ev, **kw):
        return (
            ev.type in self.execute_event_types and
            self.detail == ev.detail and
            self.mods.matches(ev.state)
        )

class if_key_press(binding_base):
    execute_event_types = [X.KeyPress]

    def __init__(self, keyname, mods, **kw):
        self.keyname = keyname
        binding_base.__init__(self, None, mods, **kw)

    def _setup(self, wm, dpy):
        if hasattr(self, '_is_setup'):
            return
        self.detail = dpy.keysym_to_keycode(
            XK.string_to_keysym(self.keyname))
        self._is_setup = True

    def __call__(self, wm, **kw):
        self._setup(wm, wm.dpy)
        return binding_base.__call__(self, wm=wm, **kw)

class if_key_release(if_key_press):
    execute_event_types = [X.KeyRelease]

class if_button_press(binding_base):
    execute_event_types = [X.ButtonPress]

class if_button_release(if_button_press):
    execute_event_types = [X.ButtonRelease]

