# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.base_config import *

import socket

def corn(cmd):
    return 'dbus-send --session --type=method_call --dest=org.mpris.corn '\
            '/Player org.freedesktop.MediaPlayer.%s' % cmd

wm.vwidth = W * 3
wm.vheight = H * 3

chains = [
    (if_key("u",      C+A), viewport_absolute_move(  0,   0)),
    (if_key("i",      C+A), viewport_absolute_move(  W,   0)),
    (if_key("o",      C+A), viewport_absolute_move(W*2,   0)),
    (if_key("j",      C+A), viewport_absolute_move(  0,   H)),
    (if_key("k",      C+A), viewport_absolute_move(  W,   H)),
    (if_key("l",      C+A), viewport_absolute_move(W*2,   H)),
    (if_key("m",      C+A), viewport_absolute_move(  0, H*2)),
    (if_key("comma",  C+A), viewport_absolute_move(  W, H*2)),
    (if_key("period", C+A), viewport_absolute_move(W*2, H*2)),

    (if_key("Left",  C), viewport_relative_move(-W,  0)),
    (if_key("Right", C), viewport_relative_move(+W,  0)),
    (if_key("Up",    C), viewport_relative_move( 0, -H)),
    (if_key("Down",  C), viewport_relative_move( 0, +H)),

    (if_key("x", C+A), execute("urxvt")),
    (if_key("s", C+A), execute("sleep 1; xset s activate")),

    (if_key("z", M4), execute(corn("Prev"))),
    (if_key("x", M4), execute(corn("Stop"))),
    (if_key("c", M4), execute(corn("Play"))),
    (if_key("v", M4), execute(corn("Pause"))),
    (if_key("b", M4), execute(corn("Next"))),

    (if_key('w', C+A), if_manipulable, delete_client()),
    (if_button(1,  A), if_manipulable, flipping_move()),
    (if_button(3,  A), if_manipulable, flipping_resize()),
    (if_button(4,  A), if_manipulable, client_method('stack_bottom')),
    (if_button(5,  A), if_manipulable, client_method('stack_top')),

    # maximizations: full screen, left half, right half

    (if_key("f", M4), if_manipulable, ewmh.tile(0,  0, 100, 100)),
    (if_key("h", M4), if_manipulable, ewmh.tile(0,  0, 50,  100)),
    (if_key("l", M4), if_manipulable, ewmh.tile(50, 0, 50,  100)),
]

# the recursiveness of grabbing on root is also causing global keybindings to
# temporarily shift focus to root when using them.

for chain in chains:
    app.hub.attach("event", *chain)

app.run()

