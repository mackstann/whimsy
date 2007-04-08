from Xlib import X

from whimsy import props, util, signals

class net_supported:
    def startup(self, signal):
        props.change_prop(signal.wm.dpy, signal.wm.root, '_NET_SUPPORTED', [
            signal.wm.dpy.get_atom(propname)
            for propname in props.supported_props()
            if propname.startswith('_NET_')
        ])

    def shutdown(self, signal):
        signal.wm.root.delete_property('_NET_SUPPORTED')

class net_supporting_wm_check:
    def startup(self, signal):
        self.win = signal.wm.root.create_window(-2000, -2000, 1, 1, 0, X.CopyFromParent)
        props.change_prop(signal.wm.dpy, self.win, '_NET_WM_NAME', 'Whimsy')
        props.change_prop(signal.wm.dpy, self.win, '_NET_SUPPORTING_WM_CHECK', self.win.id)
        props.change_prop(signal.wm.dpy, signal.wm.root, '_NET_SUPPORTING_WM_CHECK', self.win.id)

    def shutdown(self, signal):
        signal.wm.root.delete_property('_NET_SUPPORTING_WM_CHECK')
        self.win.delete_property('_NET_SUPPORTING_WM_CHECK')
        self.win.delete_property('_NET_WM_NAME')
        self.win.destroy()

class net_desktop_geometry:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def startup(self, signal):
        props.change_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_GEOMETRY',
            [self.width, self.height]
        )

    def shutdown(self, signal):
        signal.wm.root.delete_property('_NET_DESKTOP_GEOMETRY')

class initialize_net_desktop_viewport:
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

