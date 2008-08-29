# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.base_config import *

import socket

class mpd(object):
    'control music player daemon (http://musicpd.org)'
    def __init__(self, cmd):
        self.cmd = cmd
    def __call__(self, **kw):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', 6600))
            s.send("%s\n" % self.cmd)
            s.close()
        except socket.error:
            pass

wm.vwidth = W * 3
wm.vheight = H * 3

# def grab_button(self, button, modifiers, owner_events, event_mask, pointer_mode, keyboard_mode, confine_to, cursor, onerror = None):
# def grab_key(self,    key,    modifiers, owner_events,             pointer_mode, keyboard_mode,                     onerror = None):

def grab_key(dpy, win, key, modifier):
    from Xlib import XK, X
    for mask in modcore.every_lock_combination(modifier.match):
        win.grab_key(dpy.keysym_to_keycode(XK.string_to_keysym(key)), mask, 1, X.GrabModeAsync, X.GrabModeAsync)

def grab_button(dpy, win, button, modifier):
    from Xlib import X
    for mask in modcore.every_lock_combination(modifier.match):
        win.grab_button(button, mask, 1, X.NoEventMask, X.GrabModeAsync, X.GrabModeAsync, X.NONE, X.NONE)

def client_grab_all(hub, client, **kw):
    grab_key(client.dpy, client.win, 'u', C+A)
    grab_key(client.dpy, client.win, 'i', C+A)
    grab_key(client.dpy, client.win, 'o', C+A)
    grab_key(client.dpy, client.win, 'j', C+A)
    grab_key(client.dpy, client.win, 'k', C+A)
    grab_key(client.dpy, client.win, 'l', C+A)
    grab_key(client.dpy, client.win, 'm', C+A)
    grab_key(client.dpy, client.win, 'comma', C+A)
    grab_key(client.dpy, client.win, 'period', C+A)

    grab_key(client.dpy, client.win, 'Left', C)
    grab_key(client.dpy, client.win, 'Right', C)
    grab_key(client.dpy, client.win, 'Up', C)
    grab_key(client.dpy, client.win, 'Down', C)

    grab_key(client.dpy, client.win, 'x', C+A)
    grab_key(client.dpy, client.win, 's', C+A)

    grab_key(client.dpy, client.win, 'z', M4)
    grab_key(client.dpy, client.win, 'x', M4)
    grab_key(client.dpy, client.win, 'c', M4)
    grab_key(client.dpy, client.win, 'v', M4)
    grab_key(client.dpy, client.win, 'b', M4)

    grab_key(client.dpy, client.win, 'w', C+A)

    grab_key(client.dpy, client.win, 'f', M4)
    grab_key(client.dpy, client.win, 'h', M4)
    grab_key(client.dpy, client.win, 'l', M4)

    grab_button(client.dpy, client.win, 1, A)
    grab_button(client.dpy, client.win, 3, A)
    grab_button(client.dpy, client.win, 4, A)
    grab_button(client.dpy, client.win, 5, A)


def root_grab_all(hub, wm, dpy, **kw):
    grab_key(wm.dpy, wm.root, 'x', C+A)
    grab_key(wm.dpy, wm.root, 's', C+A)

    grab_key(wm.dpy, wm.root, 'z', M4)
    grab_key(wm.dpy, wm.root, 'x', M4)
    grab_key(wm.dpy, wm.root, 'c', M4)
    grab_key(wm.dpy, wm.root, 'v', M4)
    grab_key(wm.dpy, wm.root, 'b', M4)

    #grab_button(wm.dpy, wm.root, 1, A) # doubleclick root


app.hub.register('client_init_after', client_grab_all)
app.hub.register('wm_init_after', root_grab_all)

actions = [
    (viewport_absolute_move(  0,   0), if_key_press("u",      C+A)),
    (viewport_absolute_move(  W,   0), if_key_press("i",      C+A)),
    (viewport_absolute_move(W*2,   0), if_key_press("o",      C+A)),
    (viewport_absolute_move(  0,   H), if_key_press("j",      C+A)),
    (viewport_absolute_move(  W,   H), if_key_press("k",      C+A)),
    (viewport_absolute_move(W*2,   H), if_key_press("l",      C+A)),
    (viewport_absolute_move(  0, H*2), if_key_press("m",      C+A)),
    (viewport_absolute_move(  W, H*2), if_key_press("comma",  C+A)),
    (viewport_absolute_move(W*2, H*2), if_key_press("period", C+A)),

    (viewport_relative_move(-W,  0), if_key_press("Left",  C)),
    (viewport_relative_move(+W,  0), if_key_press("Right", C)),
    (viewport_relative_move( 0, -H), if_key_press("Up",    C)),
    (viewport_relative_move( 0, +H), if_key_press("Down",  C)),

    (execute("aterm"), if_key_press("x", C+A)),
    (execute("aterm"), if_root, if_button_press(1, Any), if_doubleclick),

    (execute("sleep 1; xset s activate"), if_key_press("s", C+A)),

    (mpd("previous"), if_key_press("z", M4)),
    (mpd("stop"),     if_key_press("x", M4)),
    (mpd("play"),     if_key_press("c", M4)),
    (mpd("pause"),    if_key_press("v", M4)),
    (mpd("next"),     if_key_press("b", M4)),

    #(client_method('focus'), if_client, if_button_press(1, Any, passthrough=True)),
    (delete_client(),        if_client, if_key_press('w', C+A)),
    (start_move(),           if_button_press(1, A), if_client),
    (start_resize(),         if_button_press(3, A), if_client),
    (client_method('stack_bottom'), if_button_press(4, A), if_client),
    (client_method('stack_top'),    if_button_press(5, A), if_client),

    # maximizations: full screen, left half, right half

    (client_method('moveresize', x=0,   y=0, width=W,   height=H),
     if_key_press("f", M4)),

    (client_method('moveresize', x=0,   y=0, width=W/2, height=H),
     if_key_press("h", M4)),

    (client_method('moveresize', x=W/2, y=0, width=W/2, height=H),
     if_key_press("l", M4)),
]

for action in actions:
    app.hub.register("event", action[0], *action[1:])

import os.path
app.log_filename = os.path.expanduser("~/.whimsy.log")
app.run()

