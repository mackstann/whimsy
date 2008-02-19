# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from whimsy import props
from whimsy.log import *

from Xlib import error as Xerror

def move_all_clients_relative(wm, x, y):
    if x or y:
        for c in wm.clients:
            debug("moving %r %r" % (c.props['WM_NAME'], c.props['WM_CLASS']))
            c.moveresize_rel(x=x, y=y)
            c.wm.dpy.sync()

def move_viewport_to(wm, current_x, current_y, to_x, to_y):
    props.change_prop(wm.dpy, wm.root, '_NET_DESKTOP_VIEWPORT', [to_x, to_y])
    if current_x != to_x or current_y != to_y:
        move_all_clients_relative(wm, current_x - to_x, current_y - to_y)
        #discard enternotifies

