# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from Xlib import X, Xutil
from Xlib import error as Xerror

from itertools import *

from whimsy import event, util, modifiers, props

from whimsy.log import *
from whimsy.client import managed_client

from whimsy.x_event_manager import x_event_manager
from whimsy import signals

from whimsy.window_manager import util

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

        self.root = dpy.screen().root
        self.focus = X.NONE

        self.clients = []

        self.signal("wm_init_before")

        self.ecore = event.event_core()
        self.modcore = modifiers.modifier_core(dpy)

        self.signal("wm_init_after")

    # x_event_manager virtual method
    def process_one_event(self):
        self.signal("xevent", xev=self.next_event())

    # MOVE TO SCREEN CLASS?

    def shutdown(self):
        self.signal("wm_shutdown_before")
        self.root.change_attributes(event_mask=X.NoEventMask)
        self.shutdown_all()
        self.running = False
        self.signal("wm_shutdown_after")

    def manage(self):
        self.signal("wm_manage_before")
        self.get_wm_selection()
        self.manage_all()
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

    def manage_all(self):
        self.clients = [
            managed_client(self, win)
            for win in self.root.query_tree().children
            if self.should_manage_existing_window(win)
        ]

    def shutdown_all(self):
        while self.clients:
            self.clients.pop().shutdown()

    def should_manage_existing_window(self, win):
        attr = win.get_attributes()
        return (
            not attr.override_redirect
            and attr.map_state == X.IsViewable
            and getattr(win.get_wm_hints(), 'initial_state', 'nope')
                == Xutil.NormalState
        )

    def should_manage_new_window(self, win):
        return not win.get_attributes().override_redirect

    def window_to_client(self, win):
        return self.window_id_to_client(win.id)

    def window_id_to_client(self, wid):
        for client in self.clients:
            if wid == client.win.id:
                return client

    def set_focus(self, win):
        if self.focus != win:
            self.dpy.set_input_focus(win, X.RevertToPointerRoot, X.CurrentTime)
            self.focus = win


