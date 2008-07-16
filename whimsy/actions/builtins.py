# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, subprocess, logging

from whimsy.x11 import props

def _unmanage(hub, wm, win, delete=False, **kw):
    c = wm.window_to_client(win)
    hub.signal('before_unmanage_window', client=c, win=win)
    if c:
        wm.clients.remove(c)
        c.shutdown()
        if delete:
            c.delete()
    hub.signal('after_unmanage_window', win=win)

class unmanage_window(object):
    def __call__(self, **kw):
        _unmanage(**kw)

class delete_client(object):
    def __call__(self, **kw):
        _unmanage(delete=True, **kw)


# _WHIMSY_CLIENT_LIST_FOCUS: lists managed windows that have been
# focused, most recent first

class update_client_list_focus(object):
    def __call__(self, wm, win, **kw):
        wins = props.get_prop(wm.dpy, wm.root, '_WHIMSY_CLIENT_LIST_FOCUS')
        try:
            wins.remove(win.id)
        except ValueError:
            pass
        wins.insert(0, win.id)
        props.change_prop(wm.dpy, wm.root, '_WHIMSY_CLIENT_LIST_FOCUS', wins)

class focus_last_focused(object):
    def __call__(self, wm, win, **kw):
        wins = props.get_prop(wm.dpy, wm.root, '_WHIMSY_CLIENT_LIST_FOCUS')
        while wins:
            c = wm.window_id_to_client(wins[0])
            if c:
                c.focus()
                break
            wins.pop(0)
        props.change_prop(wm.dpy, wm.root, '_WHIMSY_CLIENT_LIST_FOCUS', wins)

class client_method(object):
    def __init__(self, methodname, *a, **kw):
        self.methodname = methodname
        self.a = a
        self.kw = kw

    def __call__(self, wm, **kw):
        if 'client' in kw:
            c = kw['client']
        else:
            c = wm.window_to_client(kw['win'])
        getattr(c, self.methodname)(*self.a, **self.kw)

class execute(object):
    def __init__(self, cmd):
        self.cmd = cmd
    def __call__(self, **kw):
        if not os.fork():
            os.setsid()
            subprocess.Popen(['/bin/sh', '-c', self.cmd], close_fds=True)
            os._exit(0)

class viewport_absolute_move(object):
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __call__(self, hub, wm, **kw):
        to_x, to_y = self.x, self.y

        if not wm.can_move_viewport_to(to_x, to_y):
            logging.error("viewport_absolute_move: can't move to %r; "
                "desktop isn't big enough" % ((to_x, to_y)))
            return

        current_x = wm.vx
        current_y = wm.vy

        if (current_x, current_y) == (to_x, to_y):
            return

        xdelta = current_x - to_x
        ydelta = current_y - to_y

        for c in wm.clients:
            c.moveresize_rel(x=xdelta, y=ydelta)
            #c.dpy.sync() # necessary?  maybe not
            #wish list: discard enternotifies

        hub.signal('after_viewport_move', x=to_x, y=to_y)

class viewport_relative_move(object):
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __call__(self, wm, **kw):
        current_x = wm.vx
        current_y = wm.vy

        if wm.can_move_viewport_by(self.x, self.y):
            viewport_absolute_move(current_x+self.x, current_y+self.y)(wm=wm, **kw)

class discover_existing_windows(object):
    def __call__(self, hub, wm, **kw):
        for win in wm.root.query_tree().children:
            hub.signal('existing_window_discovered', win=win)

