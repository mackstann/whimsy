# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy import util
from whimsy.x11 import props

class update_client_property(object):
    def __call__(self, wm, win, ev, **kw):
        propname = wm.dpy.get_atom_name(ev.atom)
        if propname in props.supported_props():
            wm.window_to_client(win).update_prop(propname)

# todo: click focus handler & sloppy focus handler

#todo: circulate request
class configure_request_handler(object):
    def __call__(self, wm, win, ev, **kw):
        client_or_win = wm.window_to_client(win) or win
        client_or_win.configure(**util.configure_request_changes(ev))

class install_colormap(object):
    def __call__(self, ev, **kw):
        ev.colormap.install_colormap()

