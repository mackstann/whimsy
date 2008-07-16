# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy import util
from whimsy.x11 import props

class net_supported(object):
    def startup(self, wm, **kw):
        props.change_prop(wm.dpy, wm.root, '_NET_SUPPORTED', [
            wm.dpy.get_atom('_' + attr.upper())
            for attr in globals().keys()
            if attr.startswith('net_')
        ])

    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_SUPPORTED')

class net_client_list(object):
    def __init__(self):
        self.win_ids = []

    @classmethod
    def propname(cls):
        return '_'+cls.__name__.upper()

    def change_prop(self, wm):
        props.change_prop(wm.dpy, wm.root, self.propname(), self.win_ids)

    def add_window(self, wm, win, **kw):
        self.win_ids.insert(0, win.id)
        self.change_prop(wm)

    def remove_window(self, wm, win, **kw):
        self.win_ids.remove(win.id)
        self.change_prop(wm)

    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, self.propname())

class net_client_list_stacking(net_client_list):
    def raise_window(self, wm, win, **kw):
        self.win_ids.remove(win.id)
        self.win_ids.insert(0, win.id)
        self.change_prop(wm)

    def lower_window(self, wm, win, **kw):
        self.win_ids.remove(win.id)
        self.win_ids.append(win.id)
        self.change_prop(wm)

class net_number_of_desktops(object):
    def startup(self, wm, **kw):
        props.change_prop(wm.dpy, wm.root, '_NET_NUMBER_OF_DESKTOPS', 1)
    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_NUMBER_OF_DESKTOPS')

class net_desktop_geometry(object):
    def startup(self, wm, **kw):
        props.change_prop(
            wm.dpy, wm.root, '_NET_DESKTOP_GEOMETRY',
            [wm.vwidth, wm.vheight]
        )

    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_DESKTOP_GEOMETRY')

class net_desktop_viewport(object):
    def startup(self, hub, wm, **kw):
        viewport = props.get_prop(wm.dpy, wm.root,
            '_NET_DESKTOP_VIEWPORT')

        if not viewport:
            viewport = [0, 0]
            props.change_prop(wm.dpy, wm.root,
                '_NET_DESKTOP_VIEWPORT', viewport)

        hub.signal('viewport_discovered', x=viewport[0], y=viewport[1])

    def refresh(self, wm, x, y, **kw):
        props.change_prop(
            wm.dpy, wm.root, '_NET_DESKTOP_VIEWPORT',
            [x, y]
        )

class net_current_desktop(object):
    def startup(self, wm, **kw):
        props.change_prop(wm.dpy, wm.root, '_NET_CURRENT_DESKTOP', 0)
    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_CURRENT_DESKTOP')

class net_desktop_names(object):
    def startup(self, wm, **kw):
        props.change_prop(wm.dpy, wm.root, '_NET_DESKTOP_NAMES', [])
    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_DESKTOP_NAMES')

# _NET_ACTIVE_WINDOW
# _NET_WORKAREA

class net_supporting_wm_check(object):
    def startup(self, wm, **kw):
        self.win = wm.root.create_window(-5000, -5000, 1, 1, 0, X.CopyFromParent)
        props.change_prop(wm.dpy, self.win, '_NET_WM_NAME', 'Whimsy')
        props.change_prop(wm.dpy, self.win, '_NET_SUPPORTING_WM_CHECK', self.win.id)
        props.change_prop(wm.dpy, wm.root, '_NET_SUPPORTING_WM_CHECK', self.win.id)

    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_SUPPORTING_WM_CHECK')
        props.delete_prop(wm.dpy, self.win, '_NET_SUPPORTING_WM_CHECK')
        props.delete_prop(wm.dpy, self.win, '_NET_WM_NAME')
        self.win.destroy()

# _NET_VIRTUAL_ROOTS
# _NET_DESKTOP_LAYOUT
# _NET_SHOWING_DESKTOP
# _NET_CLOSE_WINDOW
# _NET_MOVERESIZE_WINDOW
# _NET_WM_MOVERESIZE
# _NET_RESTACK_WINDOW
# _NET_REQUEST_FRAME_EXTENTS
# _NET_WM_NAME
# _NET_WM_VISIBLE_NAME
# _NET_WM_ICON_NAME
# _NET_WM_VISIBLE_ICON_NAME
# _NET_WM_DESKTOP
# _NET_WM_WINDOW_TYPE
# _NET_WM_STATE
# _NET_WM_ALLOWED_ACTIONS
# _NET_WM_STRUT
# _NET_WM_STRUT_PARTIAL
# _NET_WM_ICON_GEOMETRY
# _NET_WM_ICON
# _NET_WM_PID
# _NET_WM_HANDLED_ICONS
# _NET_WM_USER_TIME
# _NET_FRAME_EXTENTS
# _NET_WM_PING
# _NET_WM_SYNC_REQUEST


