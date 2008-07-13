# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy import util
from whimsy.x11 import props

class net_supported(object):
    def startup(self, wm, **kw):
        props.change_prop(wm.dpy, wm.root, '_NET_SUPPORTED', [
            wm.dpy.get_atom(propname)
            for propname in props.supported_props()
            if propname.startswith('_NET_')
        ])

    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_SUPPORTED')

class net_number_of_desktops(object):
    def startup(self, wm, **kw):
        props.change_prop(wm.dpy, wm.root, '_NET_NUMBER_OF_DESKTOPS', 1)
    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_NUMBER_OF_DESKTOPS')

class net_current_desktop(object):
    def startup(self, wm, **kw):
        props.change_prop(wm.dpy, wm.root, '_NET_CURRENT_DESKTOP', 0)
    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_CURRENT_DESKTOP')

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

class net_desktop_geometry(object):
    def startup(self, wm, **kw):
        props.change_prop(
            wm.dpy, wm.root, '_NET_DESKTOP_GEOMETRY',
            [wm.vwidth, wm.vheight]
        )

    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_DESKTOP_GEOMETRY')

class net_client_list(object):
    def refresh(self, wm, **kw):
        props.change_prop(
            wm.dpy, wm.root, '_NET_CLIENT_LIST',
            [ c.win.id for c in wm.clients ]
        )

    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, '_NET_CLIENT_LIST')

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

