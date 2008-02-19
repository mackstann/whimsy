# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy import util, client, signals, props
from whimsy.log import *

class update_client_property:
    def __call__(self, signal):
        propname = signal.wm.dpy.get_atom_name(signal.ev.atom)
        if propname not in props.supported_props():
            return
        signal.wm.window_to_client(signal.ev.window).update_prop(propname)

# todo: click focus handler & sloppy focus handler

# XXX overlap with delete_client
class remove_client:
    def __call__(self, signal):
        signal.wm.clients.remove(
            signal.wm.window_to_client(signal.ev.window)
        )
        signal.wm.signal('after_remove_client', win=signal.ev.window)

#todo: circulate request
class configure_request_handler:
    def __call__(self, signal):
        (
            signal.wm.window_to_client(signal.ev.window)
            or signal.ev.window
        ).configure(
            **util.configure_request_changes(signal.ev)
        )

class install_colormap:
    def __call__(self, signal):
        signal.ev.colormap.install_colormap()

