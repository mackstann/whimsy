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

chains = [
    (if_key_press("u",      C+A), viewport_absolute_move(  0,   0)),
    (if_key_press("i",      C+A), viewport_absolute_move(  W,   0)),
    (if_key_press("o",      C+A), viewport_absolute_move(W*2,   0)),
    (if_key_press("j",      C+A), viewport_absolute_move(  0,   H)),
    (if_key_press("k",      C+A), viewport_absolute_move(  W,   H)),
    (if_key_press("l",      C+A), viewport_absolute_move(W*2,   H)),
    (if_key_press("m",      C+A), viewport_absolute_move(  0, H*2)),
    (if_key_press("comma",  C+A), viewport_absolute_move(  W, H*2)),
    (if_key_press("period", C+A), viewport_absolute_move(W*2, H*2)),

    (if_key_press("Left",  C), viewport_relative_move(-W,  0)),
    (if_key_press("Right", C), viewport_relative_move(+W,  0)),
    (if_key_press("Up",    C), viewport_relative_move( 0, -H)),
    (if_key_press("Down",  C), viewport_relative_move( 0, +H)),

    (if_key_press("x", C+A), execute("aterm")),

    (if_key_press("s", C+A), execute("sleep 1; xset s activate")),

    (if_key_press("z", M4), mpd("previous")),
    (if_key_press("x", M4), mpd("stop")),
    (if_key_press("c", M4), mpd("play")),
    (if_key_press("v", M4), mpd("pause")),
    (if_key_press("b", M4), mpd("next")),

    #(client_method('focus'), if_client, if_button_press(1, Any, passthrough=True)),
    (if_client, if_key_press('w', C+A), delete_client()),
    (if_client, if_button_press(1, A), start_move()),
    (if_client, if_button_press(3, A), start_resize()),
    (if_client, if_button_press(4, A), client_method('stack_bottom')),
    (if_client, if_button_press(5, A), client_method('stack_top')),

    # maximizations: full screen, left half, right half

    (if_key_press("f", M4), if_client, client_method('moveresize', x=0,   y=0, width=W,   height=H)),
    (if_key_press("h", M4), if_client, client_method('moveresize', x=0,   y=0, width=W/2, height=H)),
    (if_key_press("l", M4), if_client, client_method('moveresize', x=W/2, y=0, width=W/2, height=H)),
]

# the recursiveness of grabbing on root is also causing global keybindings to
# temporarily shift focus to root when using them.

for chain in chains:
    app.hub.register("event", *chain)
    for func in chain:
        if isinstance(func, binding_base):
            if if_client not in chain:
                app.hub.register('wm_manage_after', func.grab)
            if if_root not in chain:
                app.hub.register('client_init_after', func.grab)

app.run()

