# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

# the github link to this file has been added to
# <http://www.freedesktop.org/wiki/Specifications/wm-spec>, so if the location
# of this file changes within the repository, be sure to update that page

import inspect
from Xlib import X

from whimsy import util
from whimsy.x11 import props

class ewmh_prop(object):
    also_implements = ()
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
        for name, attr in globals().items():
            if not name.startswith('net_'):
                continue

            if ewmh_prop in inspect.getmro(attr):
                supported.append(wm.dpy.get_atom('_' + name.upper()))
                supported += [
                    wm.dpy.get_atom(a) for a in attr.also_implements
                ]

        self.set(supported + [wm.dpy.get_atom('_NET_SHOWING_DESKTOP')]) # XXX hack

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


# _NET_VIRTUAL_ROOTS n/a

# _NET_DESKTOP_LAYOUT ignored
# "The Window Manager may use this layout information or may choose to ignore
# it."

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

def make_strut(wm, prop_data):
    keys = '''left right top bottom left_start_y left_end_y right_start_y
    right_end_y top_start_x top_end_x bottom_start_x bottom_end_x'''.split()

    bottom = wm.root_geometry.height
    right = wm.root_geometry.width

    defaults_for_non_partial_struts = [0, bottom, 0, bottom, 0, right, 0, right]

    return dict(zip(
        keys,
        prop_data + (
            defaults_for_non_partial_struts if len(prop_data) == 4 else []
        )
    ))

class net_wm_strut_partial(ewmh_prop):
    also_implements = '_NET_WM_STRUT', '_NET_WORKAREA'
    def __init__(self, hub, wm):
        super(net_wm_strut_partial, self).__init__(hub, wm)
        self.struts = {}
        hub.attach('after_manage_window', self.check)
        hub.attach('after_unmanage_window', self.remove_client)
        hub.attach('client_property_updated', self.property_updated)

    def check(self, wm, client, **kw):
        # these will trigger our property_updated()
        client.update_prop('_NET_WM_STRUT_PARTIAL')
        client.update_prop('_NET_WM_STRUT')

    def property_updated(self, hub, wm, client, propname, **kw):
        if '_NET_WM_STRUT_PARTIAL' in client.props:
            prop_data = client.props['_NET_WM_STRUT_PARTIAL']
        elif '_NET_WM_STRUT' in client.props:
            prop_data = client.props['_NET_WM_STRUT']
        else:
            return

        if prop_data == [0] * len(prop_data):
            if client.win.id in self.struts:
                del self.struts[client.win.id]
        else:
            new_strut = make_strut(wm, prop_data)
            if new_strut == self.struts.get(client.win.id):
                return
            self.struts[client.win.id] = new_strut

        self.update_workarea(hub, wm)

    def remove_client(self, hub, wm, win, **kw):
        if win.id in self.struts:
            del self.struts[win.id]
            # this makes clients think they need to make way for the struts,
            # even though the struts are going away.
            self.update_workarea(hub, wm)

    def update_workarea(self, hub, wm):
        margin_left = margin_right = margin_top = margin_bottom = 0
        if self.struts:
            margin_left   = max(map(lambda s: s['left'],   self.struts.values()))
            margin_right  = max(map(lambda s: s['right'],  self.struts.values()))
            margin_top    = max(map(lambda s: s['top'],    self.struts.values()))
            margin_bottom = max(map(lambda s: s['bottom'], self.struts.values()))

        workarea = (
            margin_left, # x of workarea box, and..
            margin_top,  # y
            wm.root_geometry.width - (margin_left + margin_right),  # width
            wm.root_geometry.height - (margin_top + margin_bottom), # height
        )
        props.change_prop(wm.dpy, wm.root, '_NET_WORKAREA', workarea)

        hub.emit('workarea_changed',
            **dict(zip(('x', 'y', 'width', 'height'), workarea)))

def confine_to_workarea(hub, wm, x, y, width, height, **kw):
    # this should go somewhere else

    # need to differentiate between encroaching and retreating/disappearing

    clients = [ c for c in wm.clients if not c.out_of_viewport(wm) ]

    #left edge
    for c in clients:
        if c.props.get('_NET_WM_STRUT') or c.props.get('_NET_WM_STRUT_PARTIAL'):
            continue

        def fix_axis(begin, size, wm_size, work_begin, work_size):
            near_movable    = 0 <= c.geom[begin]
            near_needs_move = 0 <= c.geom[begin] < work_begin
            far_movable     =                        c.geom[begin]+c.geom[size] <= wm_size
            far_needs_move  = work_begin+work_size < c.geom[begin]+c.geom[size] <= wm_size

            if near_needs_move:
                c.geom[begin] = work_begin
                if far_movable:
                    c.geom[size] = min(c.geom[size], work_size)
            elif far_needs_move:
                c.geom[begin] -= (c.geom[begin]+c.geom[size]) - (work_begin+work_size)
                if near_movable:
                    near_overlap = work_begin - c.geom[begin]
                    if near_overlap > 0:
                        c.geom[begin] += near_overlap
                        c.geom[size] -= near_overlap

        fix_axis(0, 2, wm.root_geometry.width, x, width)
        fix_axis(1, 3, wm.root_geometry.height, y, height)

        c.moveresize()


# 'send_event': True,
# 'type': 33,
# 'window': <Xlib.display.Window 0x00400002>,
# 'client_type': 269, # message type!
# 'data': (32, array('L', [
#        2L,          # source.  1=app, 2=pager
#        2162957220L, # time
#        0L,          # requestor's active window
#        0L,
#        0L
#    ])),
# 'sequence_number': 3509

def message_type(ev):
    # Xlib had/has a typo.  support the old broken version and the future fixed
    # version.
    try:
        return ev.message_type # correct
    except AttributeError:
        return ev.client_type

def handle_client_message(wm, ev, **kw):
    #_NET_ACTIVE_WINDOW = 269
    type = message_type(ev)
    if type == wm.dpy.get_atom('_NET_ACTIVE_WINDOW'):
        handle_net_active_window_message(wm=wm, ev=ev, **kw)
    elif type == wm.dpy.get_atom('_NET_SHOWING_DESKTOP'):
        handle_net_showing_desktop_message(wm=wm, ev=ev, **kw)

def handle_net_active_window_message(wm, ev, **kw):
    win = ev.window
    c = wm.find_client(win)
    if not c:
        return
    c.focus()
    c.stack_top()

def handle_net_showing_desktop_message(wm, ev, **kw):
    if ev.data[1][0]:
        print "iconifying everything"
    else:
        print "de-iconifying everything"
    props.change_prop(wm.dpy, wm.root, '_NET_SHOWING_DESKTOP', ev.data[1][0])
    for c in wm.clients:
        if ev.data[1][0]:
            if wm.dpy.get_atom('_NET_WM_WINDOW_TYPE_DOCK') not in c.fetch_prop('_NET_WM_WINDOW_TYPE'):
                c.iconify()
        else:
            print "maybe map client"
            if wm.dpy.get_atom('_NET_WM_WINDOW_TYPE_DOCK') not in c.fetch_prop('_NET_WM_WINDOW_TYPE'):
                print "really map"
                c.map_normal()

# _NET_WM_ICON_GEOMETRY
# _NET_WM_ICON
# _NET_WM_PID
# _NET_WM_HANDLED_ICONS
# _NET_WM_USER_TIME
# _NET_FRAME_EXTENTS
# _NET_WM_PING
# _NET_WM_SYNC_REQUEST


