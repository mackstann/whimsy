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
    (execute("aterm"), if_root, if_button_press(1, Any), if_doubleclick),

    (execute("sleep 1; xset s activate"), if_key_press("s", C+A)),

    (execute("sh $HOME/scripts/mpc_osd.sh prev"), if_key_press("z", M4)),
    (execute("mpc stop"),                             if_key_press("x", M4)),
    (execute("sh $HOME/scripts/mpc_osd.sh play"),     if_key_press("c", M4)),
    (execute("mpc pause"),                            if_key_press("v", M4)),
    (execute("sh $HOME/scripts/mpc_osd.sh next"),     if_key_press("b", M4)),
    (execute("sh $HOME/scripts/killsong.sh; sh $HOME/scripts/mpc_osd.sh next"),     if_key_press("k", M4)),

    (client_method('focus'), if_client, if_button_press(1, Any, passthrough=True)),
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

import os.path, pprint
app.log_filename = os.path.expanduser("~/.whimsy.log")
try:
    app.run()
except Exception, e:
    print "class name of exception: %r" % e.__class__.__name__
    print "repr of exception: %r" % e
    print "str of exception: %s" % e
    print "__dict__ of exception:", pprint.pformat(e.__dict__)
    print "vars of exception:", pprint.pformat(vars(e))
    raise

