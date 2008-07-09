# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy import infrastructure, signals
from whimsy.actions.builtins import *
from whimsy.actions.event_handling import *
from whimsy.filters.bindings import *
from whimsy.filters import *
from whimsy.infrastructure.modifiers import *

# there are some distinct sections in this file which have emerged over time
# and should be split up at some point.  they are enumerated below as comments

### SECTION 1 - initialization

from Xlib import display

from whimsy.window_manager import window_manager
from whimsy.x_event_controller import x_event_controller
from whimsy.tick_controller import tick_controller

infrastructure.set_display_env()

dpy = display.Display()
hub = signals.publisher()

wm = window_manager(hub, dpy)
xec = x_event_controller(hub, dpy)
ticker = tick_controller(hub)

hub.defaults['wm'] = wm
hub.defaults['hub'] = hub

### SECTION 2 - internal, mostly uninteresting signal/event handling registration

from Xlib import X

from whimsy import event
from whimsy.actions import ewmh

hub.register('quit', ticker.stop)
hub.register('tick', xec.select_and_emit_all)

root_geometry = wm.root.get_geometry()
W = root_geometry.width
H = root_geometry.height

startup_shutdown_signal_methods = {
    'wm_manage_after': 'startup',
    'wm_shutdown_before': 'shutdown',
}

methods = hub.register_methods

methods(ewmh.net_supported(),                startup_shutdown_signal_methods)
methods(ewmh.net_supporting_wm_check(),      startup_shutdown_signal_methods)
methods(ewmh.net_number_of_desktops(),       startup_shutdown_signal_methods)
methods(ewmh.net_current_desktop(),          startup_shutdown_signal_methods)
methods(ewmh.net_desktop_geometry(W*3, H*3), startup_shutdown_signal_methods)

methods(ewmh.net_client_list(), {
    'after_manage_window': 'refresh',
    'after_unmanage_window': 'refresh',
    'wm_shutdown_before': 'shutdown',
})

methods(ewmh.net_desktop_viewport(), {
    'wm_manage_after': 'startup',
    'after_viewport_move': 'refresh',
})

hub.register('wm_manage_after',            discover_existing_windows())
hub.register('existing_window_discovered', manage_window(), [ if_should_manage_existing_window ])
hub.register('event', manage_window(),             [ if_(X.MapRequest,     wintype="unmanaged"), if_should_manage_new_window ])
hub.register('event', client_method('focus'),      [ if_(X.MapRequest,     wintype='client') ])
hub.register('event', client_method('focus'),      [ if_(X.EnterNotify,    wintype='client'), if_state(~ButtonMask) ])
hub.register('event', unmanage_window(),           [ if_(X.DestroyNotify,  wintype='client') ])
hub.register('event', unmanage_window(),           [ if_(X.UnmapNotify,    wintype='client') ])
hub.register('event', update_client_list_focus(),  [ if_(X.FocusIn,        wintype='client') ])
hub.register('event', update_client_property(),    [ if_(X.PropertyNotify, wintype='client') ])
hub.register('event', focus_last_focused(),        [ if_(X.DestroyNotify)    ])
hub.register('event', install_colormap(),          [ if_(X.ColormapNotify)   ])
hub.register('event', configure_request_handler(), [ if_(X.ConfigureRequest) ])
hub.register('event', update_last_button_press(),  [ if_(X.ButtonPress)      ])

hub.register('client_init_after', client_method('configure', border_width=0))
hub.register('client_init_after', client_method('map_normal'))

hub.register('event_done', event.smart_replay(),
    [ if_event_type(X.KeyPress, X.KeyRelease, X.ButtonPress, X.ButtonRelease) ]
)

### SECTION 3 - the playground

# how to focus root now?

class mpd:
    def __init__(self, cmd):
        self.cmd = cmd
    def __call__(self, ev):
        from whimsy.actions.misc import socksend
        socksend('localhost', 6600, "%s\n" % self.cmd)

actions = [
    (viewport_absolute_move(  0,   0), [ if_key_press("u",      C+A) ]),
    (viewport_absolute_move(  W,   0), [ if_key_press("i",      C+A) ]),
    (viewport_absolute_move(W*2,   0), [ if_key_press("o",      C+A) ]),
    (viewport_absolute_move(  0,   H), [ if_key_press("j",      C+A) ]),
    (viewport_absolute_move(  W,   H), [ if_key_press("k",      C+A) ]),
    (viewport_absolute_move(W*2,   H), [ if_key_press("l",      C+A) ]),
    (viewport_absolute_move(  0, H*2), [ if_key_press("m",      C+A) ]),
    (viewport_absolute_move(  W, H*2), [ if_key_press("comma",  C+A) ]),
    (viewport_absolute_move(W*2, H*2), [ if_key_press("period", C+A) ]),

    (viewport_relative_move(-W,  0),   [ if_key_press("Left",  C) ]),
    (viewport_relative_move(+W,  0),   [ if_key_press("Right", C) ]),
    (viewport_relative_move( 0, -H),   [ if_key_press("Up",    C) ]),
    (viewport_relative_move( 0, +H),   [ if_key_press("Down",  C) ]),

    (execute("aterm"), [ if_key_press("x", C+A) ]),
    (execute("aterm"), [ if_root, if_button_press(1, Any), if_multiclick(2) ]),

    (execute("sleep 1; xset s activate"), [ if_key_press("s", C+A) ]),

    (mpd("previous"), [ if_key_press("z", M4) ]),
    (mpd("stop"),     [ if_key_press("x", M4) ]),
    (mpd("play"),     [ if_key_press("c", M4) ]),
    (mpd("pause"),    [ if_key_press("v", M4) ]),
    (mpd("next"),     [ if_key_press("b", M4) ]),

    (client_method('focus'),        [ if_client, if_button_press(1, Any, passthru=True) ]),
    (delete_client(),               [ if_client, if_key_press('w', C+A) ]),
    (start_move(),                  [ if_button_press(1, A), if_client ]),
    (start_resize(),                [ if_button_press(3, A), if_client ]),
    (client_method('stack_bottom'), [ if_button_press(4, A), if_client ]),
    (client_method('stack_top'),    [ if_button_press(5, A), if_client ]),

    # maximizations: full screen, left half, right half
    (client_method('moveresize', x=0,   y=0, width=W,   height=H), [ if_key_press("f", M4) ]),
    (client_method('moveresize', x=0,   y=0, width=W/2, height=H), [ if_key_press("h", M4) ]),
    (client_method('moveresize', x=W/2, y=0, width=W/2, height=H), [ if_key_press("l", M4) ]),
]

for action, filters in actions:
    hub.register("event", action, filters)

### SECTION 4 - run the damn thing

hub.debug = True

import signal
signal.signal(signal.SIGCHLD, infrastructure.wait_signal_handler)
signal.signal(signal.SIGTERM, lambda signum, frame: ticker.stop())
signal.signal(signal.SIGINT,  lambda signum, frame: ticker.stop())
signal.signal(signal.SIGPIPE, lambda signum, frame: ticker.stop())
signal.signal(signal.SIGUSR1, lambda signum, frame: ticker.stop())
signal.signal(signal.SIGUSR2, lambda signum, frame: ticker.stop())

wm.manage()
ticker.tick_forever()

