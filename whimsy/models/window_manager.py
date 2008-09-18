# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X
from Xlib import error as Xerror

from itertools import *

from whimsy import signals
from whimsy.x11 import props
from whimsy.models import client

class wm_already_running(Exception):
    def __str__(self):
        return "Another WM appears to be running already."

class window_manager(object):
    """
    represents the window manager, which manages the specified display and
    screen (and only this screen)
    """

    mask = (
        #X.ButtonPressMask | X.ButtonReleaseMask |
        #X.KeyPressMask | X.KeyReleaseMask |
        X.EnterWindowMask | X.LeaveWindowMask |
        X.PropertyChangeMask | X.FocusChangeMask |
        X.SubstructureRedirectMask | X.SubstructureNotifyMask
    )

    running = False

    def __init__(self, hub, dpy):
        hub.emit("wm_init_before")
        self.hub = hub
        self.dpy = dpy
        self.root = dpy.screen().root
        self.root_geometry = self.root.get_geometry()
        self.vwidth = self.root_geometry.width
        self.vheight = self.root_geometry.height
        self.vx = 0
        self.vy = 0
        self.clients = []
        hub.attach('viewport_discovered', self.update_viewport)
        hub.attach('after_viewport_move', self.update_viewport)
        hub.emit("wm_init_after")

    # MOVE TO SCREEN CLASS?

    def update_viewport(self, x, y, **kw):
        self.vx = x
        self.vy = y

    def shutdown(self):
        self.hub.emit("wm_shutdown_before")
        self.root.change_attributes(event_mask=X.NoEventMask)
        self.dpy.set_input_focus(X.PointerRoot, X.RevertToPointerRoot, X.CurrentTime)
        self.shutdown_all()
        self.running = False
        self.hub.emit("wm_shutdown_after")

    def manage(self):
        self.hub.emit("wm_manage_before")
        self.get_wm_selection()
        self.running = True
        self.hub.emit("wm_manage_after")

    def get_wm_selection(self):
        catch = Xerror.CatchError(Xerror.BadAccess)
        self.root.change_attributes(event_mask=self.mask, onerror=catch)
        self.dpy.sync()
        if catch.get_error():
            raise wm_already_running()

        # TODO: ewmh selection

    def manage_window(self, win):
        try:
            c = client.managed_client(self.hub, self.dpy, win)
        except (Xerror.BadWindow, Xerror.BadDrawable):
            # it disappeared
            pass
        else:
            self.clients.append(c)
            self.hub.emit('after_manage_window', win=win, client=c)

    # move to action
    def shutdown_all(self):
        while self.clients:
            # make wm method for removing client
            self.clients.pop().shutdown()

    def find_client(self, win_or_xid):
        if hasattr(win_or_xid, 'id'):
            xid = win_or_xid.id
        else:
            xid = win_or_xid

        for client in self.clients:
            if client.win.id == xid:
                return client

    def can_move_viewport_to(self, x, y):
        total_width, total_height = props.get_prop(
            self.dpy, self.root, '_NET_DESKTOP_GEOMETRY')

        limit_x = total_width - self.root_geometry.width
        limit_y = total_height - self.root_geometry.height

        return 0 <= x <= limit_x and 0 <= y <= limit_y

    def can_move_viewport_by(self, x, y):
        current_x, current_y = props.get_prop(
            self.dpy, self.root, '_NET_DESKTOP_VIEWPORT')

        return self.can_move_viewport_to(current_x + x, current_y + y)

