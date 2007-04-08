# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from whimsy import props

def move_all_clients_relative(wm, x, y):
    for c in wm.clients:
        c.moveresize_rel(x=x, y=y)

def move_viewport_to(wm, current_x, current_y, to_x, to_y):
    props.change_prop(wm.dpy, wm.root, '_NET_DESKTOP_VIEWPORT', [to_x, to_y])
    move_all_clients_relative(wm, current_x - to_x, current_y - to_y)
    #discard enternotifies

