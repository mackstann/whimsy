from Xlib import X

from whimsy import props, util, signals

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
        self.win = signal.wm.root.create_window(-2000, -2000, 1, 1, 0, X.CopyFromParent)
        props.change_prop(signal.wm.dpy, self.win, '_NET_WM_NAME', 'Whimsy')
        props.change_prop(signal.wm.dpy, self.win, '_NET_SUPPORTING_WM_CHECK', self.win.id)
        props.change_prop(signal.wm.dpy, signal.wm.root, '_NET_SUPPORTING_WM_CHECK', self.win.id)

    def shutdown(self, signal):
        props.delete_prop(signal.wm.dpy, signal.wm.root, '_NET_SUPPORTING_WM_CHECK')
        props.delete_prop(signal.wm.dpy, self.win, '_NET_SUPPORTING_WM_CHECK')
        props.delete_prop(signal.wm.dpy, self.win, '_NET_WM_NAME')
        self.win.destroy()

class net_desktop_geometry(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def startup(self, signal):
        props.change_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_GEOMETRY',
            [self.width, self.height]
        )

    def shutdown(self, signal):
        props.delete_prop(signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_GEOMETRY')

class net_client_list(object):
    def refresh(self, signal):
        props.change_prop(
            signal.wm.dpy, signal.wm.root, '_NET_CLIENT_LIST',
            [ c.win.id for c in signal.wm.clients ]
        )

    def delete(self, signal):
        props.delete_prop(signal.wm.dpy, signal.wm.root, '_NET_CLIENT_LIST')

class initialize_net_desktop_viewport(object):
    def __call__(self, signal):
        current = props.get_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_VIEWPORT'
        )
        if not current:
            props.change_prop(
                signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_VIEWPORT',
                [0, 0]
            )
        return signals.return_code.DELETE_HANDLER

