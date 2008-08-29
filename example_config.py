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
    (execute("aterm"), if_root, if_button_press(1, Any)),# if_doubleclick),

    (execute("sleep 1; xset s activate"), if_key_press("s", C+A)),

    (mpd("previous"), if_key_press("z", M4)),
    (mpd("stop"),     if_key_press("x", M4)),
    (mpd("play"),     if_key_press("c", M4)),
    (mpd("pause"),    if_key_press("v", M4)),
    (mpd("next"),     if_key_press("b", M4)),

    #(client_method('focus'), if_client, if_button_press(1, Any, passthrough=True)),
    (delete_client(),               if_client, if_key_press('w', C+A)),
    (start_move(),                  if_client, if_button_press(1, A)),
    (start_resize(),                if_client, if_button_press(3, A)),
    (client_method('stack_bottom'), if_client, if_button_press(4, A)),
    (client_method('stack_top'),    if_client, if_button_press(5, A)),

    # maximizations: full screen, left half, right half

    (client_method('moveresize', x=0,   y=0, width=W,   height=H), if_key_press("f", M4), if_client),
    (client_method('moveresize', x=0,   y=0, width=W/2, height=H), if_key_press("h", M4), if_client),
    (client_method('moveresize', x=W/2, y=0, width=W/2, height=H), if_key_press("l", M4), if_client),
]

for action in actions:
    filters = action[1:]
    app.hub.register("event", action[0], *filters)
    for filt in filters:
        if isinstance(filt, binding_base):
            if if_client not in filters:
                app.hub.register('wm_manage_after', filt.grab)
            if if_root not in filters:
                app.hub.register('client_init_after', filt.grab)

import os.path
app.log_filename = os.path.expanduser("~/.whimsy.log")
app.run()

