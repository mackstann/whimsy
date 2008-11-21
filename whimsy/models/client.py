# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xutil
from Xlib import error as Xerror

from pygame import Rect

from whimsy import util
from whimsy.x11 import props, size_hints

class managed_client(object):

    mask = (
        #X.KeyReleaseMask | X.ButtonReleaseMask |
        X.EnterWindowMask | X.FocusChangeMask | X.PropertyChangeMask
    )

    def __init__(self, hub, dpy, win):
        self.hub = hub
        self.dpy = dpy
        self.win = win

        self.hub.emit("client_init_before", client=self)

        self.win.change_attributes(event_mask=self.mask)

        getgeom = self.win.get_geometry()
        self.geom = Rect(getgeom.x, getgeom.y, getgeom.width, getgeom.height)

        self.sizehints = size_hints.size_hints(win=self.win)

        self.props = {}

        #self.grab_all()

        self.update_prop('WM_PROTOCOLS')

        self.hub.emit("client_init_after", client=self)

    def update_prop(self, propname):
        # some properties are specified to only change at certain times (such
        # as when the window is mapped), so we keep a property cache for them
        self.props[propname] = self.fetch_prop(propname)
        self.hub.emit('client_property_updated',
            propname=propname, client=self, win=self.win)

    def fetch_prop(self, propname):
        return props.get_prop(self.dpy, self.win, propname)

    #def grab_all(self):
    #    self.win.grab_button(X.AnyButton, X.AnyModifier, 1,
    #            X.NoEventMask, X.GrabModeSync, X.GrabModeSync, X.NONE, X.NONE)
    #    self.win.grab_key(X.AnyKey, X.AnyModifier, 1, X.GrabModeSync,
    #            X.GrabModeSync)

    def map_normal(self):
        self.win.map()
        self.win.set_wm_state(state=Xutil.NormalState, icon=X.NONE)

    def moveresize(self, **kw):
        for k, v in kw.items():
            setattr(self.geom, k, v)
        self.apply_constraints()
        self.win.configure(
            x=self.geom[0],
            y=self.geom[1],
            width=self.geom[2],
            height=self.geom[3],
        )

    def apply_constraints(self):
        sh = self.sizehints
        w, h = self.geom.size
        w, h = sh.fix_min(w, h)
        w, h = sh.fix_max(w, h)
        w, h = sh.fix_increments(w, h)
        w, h = sh.fix_aspect(w, h)
        self.geom.size = w, h

    def out_of_viewport(self, wm):
        return not self.geom.colliderect(wm.root_geometry)

    def configure(self, **changes):
        self.win.configure(**changes)
        for k in "x", "y", "width", "height":
            if k in changes:
                setattr(self.geom, k, changes[k])

    def focus(self):
        self.dpy.set_input_focus(self.win, X.RevertToPointerRoot, X.CurrentTime)
        self.hub.emit('after_focus_window', client=self, win=self.win)

    def stack_top(self):
        self.win.configure(stack_mode=X.Above)
        self.hub.emit('after_raise_window', client=self, win=self.win)

    def stack_bottom(self):
        self.win.configure(stack_mode=X.Below)
        self.hub.emit('after_lower_window', client=self, win=self.win)

    def delete(self):
        wm_del = self.dpy.get_atom('WM_DELETE_WINDOW')
        catch = Xerror.CatchError(Xerror.BadWindow, Xerror.BadValue)
        if wm_del in self.props['WM_PROTOCOLS']:
            props.send_window_message(self.dpy, self.win, 'WM_PROTOCOLS', [wm_del], self.win, event_mask=0)
        else:
            self.win.kill_client()
        self.dpy.sync()


class existing_unmanaged_window(object):
    def __init__(self, win):
        self.win = win
    def should_manage(self):
        attr = self.win.get_attributes()
        return (
            not attr.override_redirect
            and attr.map_state == X.IsViewable
            and getattr(self.win.get_wm_hints(), 'initial_state', not Xutil.NormalState)
                == Xutil.NormalState
        )

class newly_mapped_window(object):
    def __init__(self, win):
        self.win = win
    def should_manage(self):
        try:
            return not self.win.get_attributes().override_redirect
        except Xerror.BadWindow:
            # it disappeared
            return False




