# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy import util
from whimsy.x11 import props

class update_client_property(object):
    def __call__(self, signal):
        propname = signal.wm.dpy.get_atom_name(signal.ev.atom)
        if propname in props.supported_props():
            signal.wm.window_to_client(signal.win).update_prop(propname)

# todo: click focus handler & sloppy focus handler

#todo: circulate request
class configure_request_handler(object):
    def __call__(self, signal):
        client_or_win = signal.wm.window_to_client(signal.win) or signal.win
        client_or_win.configure(**util.configure_request_changes(signal.ev))

class install_colormap(object):
    def __call__(self, signal):
        signal.ev.colormap.install_colormap()

