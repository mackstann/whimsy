# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.base_config import *

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

    (execute("xterm"), if_key_press("x", C+A)),
    (execute("xterm"), if_root, if_button_press(1, Any), if_doubleclick),

    (client_method('focus'), if_client, if_button_press(1, Any, passthru=True)),
    (delete_client(), if_client, if_key_press('w', C+A)),
    (start_move(),                  if_button_press(1, A), if_client),
    (start_resize(),                if_button_press(3, A), if_client),
    (client_method('stack_bottom'), if_button_press(4, A), if_client),
    (client_method('stack_top'),    if_button_press(5, A), if_client),
]

for action in actions:
    app.hub.register("event", action[0], *action[1:])

app.run()

