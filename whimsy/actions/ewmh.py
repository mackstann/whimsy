# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy import util, signals
from whimsy.x11 import props

class net_supported(object):
    def startup(self, signal):
        props.change_prop(signal.wm.dpy, signal.wm.root, '_NET_SUPPORTED', [
            signal.wm.dpy.get_atom(propname)
            for propname in props.supported_props()
            if propname.startswith('_NET_')
        ])

    def shutdown(self, signal):
        props.delete_prop(signal.wm.dpy, signal.wm.root, '_NET_SUPPORTED')

class net_number_of_desktops(object):
    def startup(self, signal):
        props.change_prop(signal.wm.dpy, signal.wm.root, '_NET_NUMBER_OF_DESKTOPS', 1)
    def shutdown(self, signal):
        props.delete_prop(signal.wm.dpy, signal.wm.root, '_NET_NUMBER_OF_DESKTOPS')

class net_current_desktop(object):
    def startup(self, signal):
        props.change_prop(signal.wm.dpy, signal.wm.root, '_NET_CURRENT_DESKTOP', 0)
    def shutdown(self, signal):
        props.delete_prop(signal.wm.dpy, signal.wm.root, '_NET_CURRENT_DESKTOP')

class net_supporting_wm_check(object):
    def startup(self, signal):
        self.win = signal.wm.root.create_window(-5000, -5000, 1, 1, 0, X.CopyFromParent)
        props.change_prop(signal.wm.dpy, self.win, '_NET_WM_NAME', 'Whimsy')
        props.change_prop(signal.wm.dpy, self.win, '_NET_SUPPORTING_WM_CHECK', self.win.id)
        props.change_prop(signal.wm.dpy, signal.wm.root, '_NET_SUPPORTING_WM_CHECK', self.win.id)

    def shutdown(self, signal):
        props.delete_prop(signal.wm.dpy, signal.wm.root, '_NET_SUPPORTING_WM_CHECK')
        props.delete_prop(signal.wm.dpy, self.win, '_NET_SUPPORTING_WM_CHECK')
        props.delete_prop(signal.wm.dpy, self.win, '_NET_WM_NAME')
        self.win.destroy()

class net_desktop_geometry(object):
    def startup(self, signal):
        props.change_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_GEOMETRY',
            [signal.wm.vwidth, signal.wm.vheight]
        )

    def shutdown(self, signal):
        props.delete_prop(signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_GEOMETRY')

class net_client_list(object):
    def refresh(self, signal):
        props.change_prop(
            signal.wm.dpy, signal.wm.root, '_NET_CLIENT_LIST',
            [ c.win.id for c in signal.wm.clients ]
        )

    def shutdown(self, signal):
        props.delete_prop(signal.wm.dpy, signal.wm.root, '_NET_CLIENT_LIST')

class net_desktop_viewport(object):
    def startup(self, signal):
        viewport = props.get_prop(signal.wm.dpy, signal.wm.root,
            '_NET_DESKTOP_VIEWPORT')

        if not viewport:
            viewport = [0, 0]
            props.change_prop(signal.wm.dpy, signal.wm.root,
                '_NET_DESKTOP_VIEWPORT', viewport)

        signal.hub.signal('viewport_discovered', x=viewport[0], y=viewport[1])

    def refresh(self, signal):
        props.change_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_VIEWPORT',
            [signal.x, signal.y]
        )

