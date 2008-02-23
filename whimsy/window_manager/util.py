# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

def move_all_clients_relative(wm, x, y):
    if x or y:
        for c in wm.clients:
            c.moveresize_rel(x=x, y=y)
            c.wm.dpy.sync()

def move_viewport_to(wm, current_x, current_y, to_x, to_y):
    if current_x != to_x or current_y != to_y:
        move_all_clients_relative(wm, current_x - to_x, current_y - to_y)
        wm.signal('after_viewport_move', x=to_x, y=to_y)
        #discard enternotifies

