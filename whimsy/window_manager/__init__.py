# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X
from Xlib import error as Xerror

from itertools import *

from whimsy import signals

class window_manager(object):
    """
    represents the window manager, which manages the specified display and
    screen (and only this screen)
    """

    mask = (
        X.ButtonPressMask | X.ButtonReleaseMask |
        X.KeyPressMask | X.KeyReleaseMask |
        X.EnterWindowMask | X.LeaveWindowMask |
        X.PropertyChangeMask | X.FocusChangeMask |
        X.SubstructureRedirectMask | X.SubstructureNotifyMask
    )

    running = False

    def __init__(self, hub, dpy):
        hub.signal("wm_init_before")
        self.hub = hub
        self.dpy = dpy
        self.root = dpy.screen().root
        self.clients = []
        hub.signal("wm_init_after")

    # MOVE TO SCREEN CLASS?

    def shutdown(self):
        self.hub.signal("wm_shutdown_before")
        self.root.change_attributes(event_mask=X.NoEventMask)
        self.dpy.set_input_focus(X.PointerRoot, X.RevertToPointerRoot, X.CurrentTime)
        self.shutdown_all()
        self.running = False
        self.hub.signal("wm_shutdown_after")

    def manage(self):
        self.hub.signal("wm_manage_before")
        self.get_wm_selection()
        self.running = True
        self.hub.signal("wm_manage_after")

    def get_wm_selection(self):
        catch = Xerror.CatchError(Xerror.BadAccess)
        self.root.change_attributes(event_mask=self.mask, onerror=catch)
        self.dpy.sync()
        if catch.get_error():
            raise RuntimeError("can't get WM selection -- another WM seems to be running")

        # TODO: ewmh selection

    # move to action
    def shutdown_all(self):
        while self.clients:
            # make wm method for removing client
            self.clients.pop().shutdown()

    # move to util?
    def window_to_client(self, win):
        return self.window_id_to_client(win.id)

    # move to util?
    def window_id_to_client(self, wid):
        for client in self.clients:
            if wid == client.win.id:
                return client

