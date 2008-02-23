# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X
from Xlib import error as Xerror

from itertools import *

from whimsy.x_event_manager import x_event_manager
from whimsy import signals

# maybe don't use inheritance for this?
class window_manager(x_event_manager, signals.publisher):
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

    def __init__(self, dpy):
        x_event_manager.__init__(self, dpy, wm=self)
        signals.publisher.__init__(self, wm=self)

        self.signal("wm_init_before")

        self.root = dpy.screen().root

        self.clients = []

        self.signal("wm_init_after")

    # x_event_manager virtual method
    def process_one_event(self):
        self.signal("xevent", xev=self.next_event())

    # MOVE TO SCREEN CLASS?

    def shutdown(self):
        self.signal("wm_shutdown_before")
        self.root.change_attributes(event_mask=X.NoEventMask)
        self.dpy.set_input_focus(X.PointerRoot, X.RevertToPointerRoot, X.CurrentTime)
        self.shutdown_all()
        self.running = False
        self.signal("wm_shutdown_after")

    def manage(self):
        self.signal("wm_manage_before")
        self.get_wm_selection()
        self.running = True
        self.signal("wm_manage_after")

    def get_wm_selection(self):
        catch = Xerror.CatchError(Xerror.BadAccess)
        self.root.change_attributes(event_mask=self.mask, onerror=catch)
        self.dpy.sync()
        if catch.get_error():
            raise RuntimeError("can't get WM selection -- another "
                               "WM seems to be running")

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

    def set_focus(self, win):
        self.dpy.set_input_focus(win, X.RevertToPointerRoot, X.CurrentTime)

