# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, subprocess, logging

from whimsy.x11 import props

def _unmanage(signal, delete=False):
    c = signal.wm.window_to_client(signal.win)
    if c:
        signal.wm.clients.remove(c)
        c.shutdown()
        if delete:
            c.delete()
    signal.hub.signal('after_unmanage_window', win=signal.win)

class unmanage_window(object):
    def __call__(self, signal):
        _unmanage(signal)

class delete_client(object):
    def __call__(self, signal):
        _unmanage(signal, delete=True)


# _WHIMSY_CLIENT_LIST_FOCUS: lists managed windows that have been
# focused, most recent first

class update_client_list_focus(object):
    def __call__(self, signal):
        wins = props.get_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS')
        try:
            wins.remove(signal.win.id)
        except ValueError:
            pass
        wins.insert(0, signal.win.id)
        props.change_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS', wins)

class focus_last_focused(object):
    def __call__(self, signal):
        wins = props.get_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS')
        while wins:
            c = signal.wm.window_id_to_client(wins[0])
            if c:
                c.focus()
                break
            wins.pop(0)
        props.change_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS', wins)

class client_method(object):
    def __init__(self, methodname, *a, **kw):
        self.methodname = methodname
        self.a = a
        self.kw = kw

    def __call__(self, signal):
        if hasattr(signal, 'client'):
            c = signal.client
        else:
            c = signal.wm.window_to_client(signal.win)
        getattr(c, self.methodname)(*self.a, **self.kw)

class execute(object):
    def __init__(self, cmd):
        self.cmd = cmd
    def __call__(self, signal):
        if not os.fork():
            os.setsid()
            subprocess.Popen(['/bin/sh', '-c', self.cmd], close_fds=True)
            os._exit(0)

class viewport_absolute_move(object):
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __call__(self, signal):
        to_x, to_y = self.x, self.y

        if not signal.wm.can_move_viewport_to(to_x, to_y):
            logging.error("viewport_absolute_move: can't move to %r; "
                "desktop isn't big enough" % ((to_x, to_y)))
            return

        current_x = signal.wm.vx
        current_y = signal.wm.vy

        if (current_x, current_y) == (to_x, to_y):
            return

        xdelta = current_x - to_x
        ydelta = current_y - to_y

        for c in signal.wm.clients:
            c.moveresize_rel(x=xdelta, y=ydelta)
            #c.dpy.sync() # necessary?  maybe not
            #wish list: discard enternotifies

        signal.hub.signal('after_viewport_move', x=to_x, y=to_y)

class viewport_relative_move(object):
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __call__(self, signal):
        current_x = signal.wm.vx
        current_y = signal.wm.vy

        if signal.wm.can_move_viewport_by(self.x, self.y):
            viewport_absolute_move(current_x+self.x, current_y+self.y)(signal)

class discover_existing_windows(object):
    def __call__(self, signal):
        for win in signal.wm.root.query_tree().children:
            signal.hub.signal('existing_window_discovered', win=win)

