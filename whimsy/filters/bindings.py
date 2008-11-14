# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, XK

class binding_base(object):
    def __init__(self, detail, mods, grabfilter=None):
        self.detail = detail
        self.mods = mods
        self.grabfilter = grabfilter
        if not grabfilter:
            self.grabfilter = lambda *a, **k: True

    def __call__(self, hub, ev, **kw):
        return (
            # type must be first because the attributes of ev depend on it
            ev.type == self.event_type and
            self.detail == ev.detail and
            self.mods.matches(ev.state) and
            self.grabfilter(hub=hub, ev=ev, **kw)
        )

    def really_grab_a_window(self, win, detail, mask):
        raise NotImplementedError

    def grab_for_window(self, wm, win, **kw):
        for mask in self.mods.every_lock_combination():
            self.really_grab_a_window(win, mask)

    def grab_for_client(self, wm, client, **kw):
        if self.grabfilter(wm=wm, win=client.win, **kw):
            self.grab_for_window(wm=wm, win=client.win, **kw)

    def __connected__(self, hub, **kw):
        hub.attach('client_init_after', self.grab_for_client)


class if_key(binding_base):
    event_type = X.KeyPress

    def __connected__(self, wm, **kw):
        # for convenience, what we initially get passed is a string of a key
        # name; convert that to a real keycode before we need to use it
        self.detail = wm.dpy.keysym_to_keycode(
            XK.string_to_keysym(self.detail))
        super(if_key, self).__connected__(wm=wm, **kw)

    def really_grab_a_window(self, win, mask):
        win.grab_key(self.detail, mask, 1, X.GrabModeAsync, X.GrabModeAsync)

class if_button(binding_base):
    event_type = X.ButtonPress

    def really_grab_a_window(self, win, mask):
        win.grab_button(self.detail, mask, 1, X.NoEventMask, X.GrabModeAsync,
                X.GrabModeAsync, X.NONE, X.NONE)
