# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.base_config import *

wm.vwidth = W * 3
wm.vheight = H * 3

actions = [
    # these take you to the nine viewports, laid out in a 3x3 grid.
    # Ctrl+Alt+...
    #     u i o
    #     j k l
    #     m , .
    # W is the screen width and H is the screen height.
    (viewport_absolute_move(  0,   0), if_key_press("u",      C+A)),
    (viewport_absolute_move(  W,   0), if_key_press("i",      C+A)),
    (viewport_absolute_move(W*2,   0), if_key_press("o",      C+A)),
    (viewport_absolute_move(  0,   H), if_key_press("j",      C+A)),
    (viewport_absolute_move(  W,   H), if_key_press("k",      C+A)),
    (viewport_absolute_move(W*2,   H), if_key_press("l",      C+A)),
    (viewport_absolute_move(  0, H*2), if_key_press("m",      C+A)),
    (viewport_absolute_move(  W, H*2), if_key_press("comma",  C+A)),
    (viewport_absolute_move(W*2, H*2), if_key_press("period", C+A)),

    # relative movements of the viewport with Ctrl+up, Ctrl+left, etc
    (viewport_relative_move(-W,  0), if_key_press("Left",  C)),
    (viewport_relative_move(+W,  0), if_key_press("Right", C)),
    (viewport_relative_move( 0, -H), if_key_press("Up",    C)),
    (viewport_relative_move( 0, +H), if_key_press("Down",  C)),

    # Ctrl+Alt+x or double click desktop (root window) to open xterm
    (execute("xterm"), if_key_press("x", C+A)),
    (execute("xterm"), if_root, if_button_press(1, Any), if_doubleclick),

    # click on client to focus
    (client_method('focus'), if_client, if_button_press(1, Any, passthrough=True)),

    # Ctrl+Alt+w to close window
    (delete_client(), if_client, if_key_press('w', C+A)),

    # Alt+left/right mouse buttons to move/resize interactively
    (start_move(),                  if_button_press(1, A), if_client),
    (start_resize(),                if_button_press(3, A), if_client),

    # Alt+wheelup to lower window, Alt+wheeldown to raise
    (client_method('stack_bottom'), if_button_press(4, A), if_client),
    (client_method('stack_top'),    if_button_press(5, A), if_client),
]

for action in actions:
    app.hub.register("event", action[0], *action[1:])

app.run()

