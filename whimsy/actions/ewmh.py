# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

# the github link to this file has been added to
# <http://www.freedesktop.org/wiki/Specifications/wm-spec>, so if the location
# of this file changes within the repository, be sure to update that page

from Xlib import X

from whimsy import util
from whimsy.x11 import props

class ewmh_prop(object):
    also_implements = []
    def __init__(self, hub, wm):
        self.wm = wm

    def propname(self):
        return '_'+self.__class__.__name__.upper()

    def get(self):
        return props.get_prop(self.wm.dpy, self.wm.root, self.propname())

    def set(self, val):
        props.change_prop(self.wm.dpy, self.wm.root, self.propname(), val)

    def delete(self):
        props.delete_prop(self.wm.dpy, self.wm.root, self.propname())

class startup_and_shutdown_with_wm(ewmh_prop):
    def __init__(self, hub, wm):
        super(startup_and_shutdown_with_wm, self).__init__(hub, wm)
        hub.attach('wm_manage_after', self.startup)
        hub.attach('wm_shutdown_before', self.shutdown)

# # # #

class net_supported(startup_and_shutdown_with_wm):
    def startup(self, wm, **kw):
        supported = []
        for attr in globals().keys():
            if isinstance(attr, ewmh_prop):
                supported.append(wm.dpy.get_atom('_' + attr.upper()))
                supported += [
                    wm.dpy.get_atom(a) for a in attr.also_implements
                ]

        self.set(supported)

    def shutdown(self, **kw):
        self.delete()

class net_number_of_desktops(startup_and_shutdown_with_wm):
    def startup(self, **kw):
        self.set(1)
    def shutdown(self, **kw):
        self.delete()

class net_current_desktop(startup_and_shutdown_with_wm):
    def startup(self, **kw):
        self.set(0)
    def shutdown(self, **kw):
        self.delete()

class net_supporting_wm_check(startup_and_shutdown_with_wm):
    def startup(self, wm, **kw):
        self.win = wm.root.create_window(-5000, -5000, 1, 1, 0, X.CopyFromParent)
        props.change_prop(wm.dpy, self.win, '_NET_WM_NAME', 'Whimsy')
        props.change_prop(wm.dpy, self.win, self.propname(), self.win.id)
        props.change_prop(wm.dpy, wm.root, self.propname(), self.win.id)

    def shutdown(self, wm, **kw):
        props.delete_prop(wm.dpy, wm.root, self.propname())
        props.delete_prop(wm.dpy, self.win, self.propname())
        props.delete_prop(wm.dpy, self.win, '_NET_WM_NAME')
        self.win.destroy()

class net_desktop_geometry(startup_and_shutdown_with_wm):
    def startup(self, wm, **kw):
        self.set([wm.vwidth, wm.vheight])
    def shutdown(self, **kw):
        self.delete()

class net_client_list(ewmh_prop):
    def __init__(self, hub, wm):
        super(net_client_list, self).__init__(hub, wm)
        self.win_ids = []
        hub.attach('after_manage_window', self.add_window)
        hub.attach('after_unmanage_window', self.remove_window)
        hub.attach('wm_shutdown_before', self.shutdown)

    def add_window(self, win, **kw):
        self.win_ids.insert(0, win.id)
        self.set(self.win_ids)

    def remove_window(self, win, **kw):
        self.win_ids.remove(win.id)
        self.set(self.win_ids)

    def shutdown(self, **kw):
        self.delete()

class net_client_list_stacking(net_client_list):
    def __init__(self, hub, wm):
        super(net_client_list_stacking, self).__init__(hub, wm)
        hub.attach('after_raise_window', self.raise_window)
        hub.attach('after_lower_window', self.lower_window)

    def raise_window(self, win, **kw):
        self.win_ids.remove(win.id)
        self.win_ids.insert(0, win.id)
        self.set(self.win_ids)

    def lower_window(self, win, **kw):
        self.win_ids.remove(win.id)
        self.win_ids.append(win.id)
        self.set(self.win_ids)

class net_desktop_viewport(ewmh_prop):
    def __init__(self, hub, wm):
        super(net_desktop_viewport, self).__init__(hub, wm)
        hub.attach('wm_manage_after', self.startup)
        hub.attach('after_viewport_move', self.refresh)

    def startup(self, hub, wm, **kw):
        viewport = self.get()

        if not viewport:
            viewport = [0, 0]
            self.set(viewport)

        hub.emit('viewport_discovered', x=viewport[0], y=viewport[1])

    def refresh(self, wm, x, y, **kw):
        self.set([x, y])

class net_desktop_names(startup_and_shutdown_with_wm):
    def startup(self, wm, **kw):
        self.set([])
    def shutdown(self, **kw):
        self.delete()

class net_active_window(ewmh_prop):
    def __init__(self, hub, wm):
        super(net_active_window, self).__init__(hub, wm)
        hub.attach('after_focus_window', self.refresh)
        hub.attach('after_focus_root', self.refresh)
        hub.attach('wm_shutdown_before', self.shutdown)

    def refresh(self, wm, **kw):
        self.set(kw['win'].id if 'win' in kw else X.NONE)

    def shutdown(self, **kw):
        self.delete()


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

# strut example:
#
# for a 50px tall, 400px wide panel that starts at x=200 and runs along the
# bottom of the screen:
#
# bottom = 50
# bottom_start_x = 200
# bottom_end_x = 599

#def make_strut(wm, prop_data):
#    keys = '''left right top bottom left_start_y left_end_y right_start_y
#    right_end_y top_start_x top_end_x bottom_start_x bottom_end_x'''.split()
#
#    defaults_for_non_partial_struts = [
#        0, wm.root_geometry.height - 1, 0, wm.root_geometry.height - 1,
#        0, wm.root_geometry.width - 1, 0, wm.root_geometry.width - 1,
#    ]
#
#    return dict(zip(
#        keys,
#        prop_data + (
#            defaults_for_non_partial_struts if len(prop_data) == 4 else []
#        )
#    ))
#
#class net_wm_strut_partial(object):
#    also_implements = '_NET_WM_STRUT', '_NET_WORKAREA'
#    def __init__(self):
#        self.struts = {}
#
#    def check(self, wm, client, win, **kw):
#        # these will trigger our update()
#        client.update_prop('_NET_WM_STRUT_PARTIAL')
#        client.update_prop('_NET_WM_STRUT')
#
#    def property_updated(self, wm, client, win, **kw):
#        prop_data = []
#        if '_NET_WM_STRUT_PARTIAL' in client.props:
#            prop_data = client.props['_NET_WM_STRUT_PARTIAL']
#        elif '_NET_WM_STRUT' in client.props:
#            prop_data = client.props['_NET_WM_STRUT']
#        if not prop_data:
#            return
#        self.struts[win.id] = make_strut(wm, prop_data)
#        self.update_workarea(wm)
#
#    def remove_client(self, wm, win, **kw):
#        if win.id in self.struts:
#            del self.struts[win.id]
#            self.update_workarea(wm)
#
#    def update_workarea(self, wm):
#        if self.struts:
#            margin_left = max(map(lambda s: s['left'], self.struts.values()))
#            margin_right = min(map(lambda s: s['right'], self.struts.values()))
#            margin_top = max(map(lambda s: s['top'], self.struts.values()))
#            margin_bottom = min(map(lambda s: s['bottom'], self.struts.values()))
#        else:
#            margin_left = margin_right = margin_top = margin_bottom = 0
#
#        props.change_prop(wm.dpy, wm.root, '_NET_WORKAREA', [
#            margin_left, margin_top,
#            wm.root_geometry.width - (margin_left + margin_right),
#            wm.root_geometry.height - (margin_top + margin_bottom),
#        ])

# _NET_WM_ICON_GEOMETRY
# _NET_WM_ICON
# _NET_WM_PID
# _NET_WM_HANDLED_ICONS
# _NET_WM_USER_TIME
# _NET_FRAME_EXTENTS
# _NET_WM_PING
# _NET_WM_SYNC_REQUEST


