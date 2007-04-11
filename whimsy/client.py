# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from Xlib import X, Xutil, error as Xerror

from whimsy import util, props

from whimsy.log import *

class managed_client:

    mask = (
        X.KeyReleaseMask |
        X.ButtonReleaseMask |
        X.EnterWindowMask | X.FocusChangeMask
    )

    def __init__(self, wm, win):
        self.wm = wm
        self.win = win

        self.wm.signal("client_init_before", client=self)

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

        self.wm.signal("client_init_after", client=self)

    def shutdown(self):
        self.win.change_attributes(event_mask=X.NoEventMask)
        self.ungrab_all()

    def update_prop(self, propname):
        self.props[propname] = props.get_prop(self.wm.dpy, self.win, propname)

    def ungrab_all(self):
        self.win.ungrab_button(X.AnyButton, X.AnyModifier)
        self.win.ungrab_key(X.AnyKey, X.AnyModifier)

    def grab_all(self):
        # should be done externally, called by signal
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
        debug('moveresize: %s' % self.geom)
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
        debug('configure: %s' % changes)
        self.win.configure(**changes)
        util.limited_dict_update(
            self.geom, changes,
            ['x', 'y', 'width', 'height'],
        )

    def focus(self):
        self.wm.set_focus(self.win)

    def stack_top(self):
        self.win.configure(stack_mode=X.Above)

    def stack_bottom(self):
        self.win.configure(stack_mode=X.Below)

    def stack_opposite(self):
        self.win.configure(stack_mode=X.Opposite)

    def delete(self):
        self.update_prop('WM_PROTOCOLS')
        wm_del = self.wm.dpy.get_atom('WM_DELETE_WINDOW')
        if wm_del in self.props['WM_PROTOCOLS']:
            props.send_window_message(self.wm.dpy, self.win, 'WM_PROTOCOLS', [wm_del], self.win, event_mask=0)
        else:
            self.win.kill_client()


