# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xutil
from Xlib import error as Xerror

from whimsy import util
from whimsy.x11 import props

class managed_client(object):

    mask = (
        X.KeyReleaseMask | X.ButtonReleaseMask |
        X.EnterWindowMask | X.FocusChangeMask
    )

    def __init__(self, hub, dpy, win):
        self.hub = hub
        self.dpy = dpy
        self.win = win

        self.hub.signal("client_init_before", client=self)

        self.win.change_attributes(event_mask=self.mask)

        self.geom = util.object_to_dict(
            self.win.get_geometry(), ['x', 'y', 'width', 'height']
        )
        self.sizehints = util.size_hints(win=self.win)

        self.props = {}

        self.grab_all()

        self.update_prop('WM_NAME')
        self.update_prop('WM_ICON_NAME')
        self.update_prop('WM_CLASS')
        self.update_prop('WM_STATE')
        self.update_prop('WM_PROTOCOLS')

        self.hub.signal("client_init_after", client=self)

    def shutdown(self):
        catch = Xerror.CatchError(Xerror.BadWindow, Xerror.BadValue) # not working...
        self.win.change_attributes(event_mask=X.NoEventMask)
        self.ungrab_all()
        self.dpy.sync()

    def update_prop(self, propname):
        # some properties are specified to only change at certain times (such
        # as when the window is mapped), so we keep a property cache for them
        self.props[propname] = self.fetch_prop(propname)

    def fetch_prop(self, propname):
        return props.get_prop(self.dpy, self.win, propname)

    def ungrab_all(self):
        self.win.ungrab_button(X.AnyButton, X.AnyModifier)
        self.win.ungrab_key(X.AnyKey, X.AnyModifier)

    def grab_all(self):
        self.win.grab_button(X.AnyButton, X.AnyModifier, X.AnyButton,
                X.NoEventMask, X.GrabModeSync, X.GrabModeSync, X.NONE, X.NONE)
        self.win.grab_key(X.AnyKey, X.AnyModifier, 1, X.GrabModeSync,
                X.GrabModeSync)

    def map_normal(self):
        self.win.map()
        self.win.set_wm_state(state=Xutil.NormalState, icon=X.NONE)

    def moveresize(self, **kw):
        self.geom.update(kw)
        self.apply_constraints()
        self.win.configure(**self.geom)

    def moveresize_rel(self, **kw):
        self.moveresize(**dict(
            (key, val + self.geom[key]) for key, val in kw.items()
        ))

    def apply_constraints(self):
        sh = self.sizehints
        w, h = self.geom['width'], self.geom['height']
        w, h = sh.fix_min(w, h)
        w, h = sh.fix_max(w, h)
        w, h = sh.fix_increments(w, h)
        w, h = sh.fix_aspect(w, h)
        self.geom['width'], self.geom['height'] = w, h

    def configure(self, **changes):
        self.win.configure(**changes)
        util.limited_dict_update(
            self.geom, changes,
            ['x', 'y', 'width', 'height'],
        )

    def focus(self):
        self.dpy.set_input_focus(self.win, X.RevertToPointerRoot, X.CurrentTime)

    def stack_top(self):
        self.win.configure(stack_mode=X.Above)

    def stack_bottom(self):
        self.win.configure(stack_mode=X.Below)

    def stack_opposite(self):
        self.win.configure(stack_mode=X.Opposite)

    def delete(self):
        wm_del = self.dpy.get_atom('WM_DELETE_WINDOW')
        catch = Xerror.CatchError(Xerror.BadWindow, Xerror.BadValue)
        if wm_del in self.props['WM_PROTOCOLS']:
            props.send_window_message(self.dpy, self.win, 'WM_PROTOCOLS', [wm_del], self.win, event_mask=0)
        else:
            self.win.kill_client()
        self.dpy.sync()




