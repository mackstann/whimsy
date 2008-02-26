# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy import event, modifiers, props, util, infrastructure, window_manager
from whimsy.actions import ewmh

from whimsy.actions.misc import socksend
from whimsy.actions.builtins import *
from whimsy.actions.event_handling import *
from whimsy.infrastructure.modifiers import *
from whimsy.filters import *
from whimsy.filters.bindings import *

wm = infrastructure.init()

root_geometry = wm.root.get_geometry()
W = root_geometry.width
H = root_geometry.height

startup_shutdown_signal_methods = {
    'wm_manage_after': 'startup',
    'wm_shutdown_before': 'shutdown',
}

wm.register_methods(ewmh.net_supported(),                startup_shutdown_signal_methods)
wm.register_methods(ewmh.net_supporting_wm_check(),      startup_shutdown_signal_methods)
wm.register_methods(ewmh.net_number_of_desktops(),       startup_shutdown_signal_methods)
wm.register_methods(ewmh.net_current_desktop(),          startup_shutdown_signal_methods)
wm.register_methods(ewmh.net_desktop_geometry(W*3, H*3), startup_shutdown_signal_methods)

wm.register_methods(ewmh.net_client_list(), {
    'after_manage_window': 'refresh',
    'after_remove_client': 'refresh',
    'after_delete_client': 'refresh',
    'wm_shutdown_before': 'shutdown',
})

wm.register_methods(ewmh.net_desktop_viewport(), {
    'wm_manage_after': 'startup',
    'after_viewport_move': 'refresh',
})

wm.register('wm_manage_after',            discover_existing_windows)
wm.register('existing_window_discovered', manage_window, [ if_should_manage_existing_window ])
wm.register('event',                      manage_window, [ if_(X.MapRequest), if_should_manage_new_window ])

wm.register('client_init_after', client_method('configure', border_width=0))
wm.register('client_init_after', client_method('map_normal'))

# how to focus root now?

act = lambda *args: wm.register("event", *args)

act(client_method('focus'),      [ if_(X.MapRequest,     'client') ])
act(client_method('focus'),      [ if_(X.EnterNotify,    'client'), if_state(~ButtonMask) ])
act(remove_client(),             [ if_(X.DestroyNotify,  'client') ])
act(remove_client(),             [ if_(X.UnmapNotify,    'client') ])
act(update_client_list_focus,    [ if_(X.FocusIn,        'client') ])
act(update_client_property(),    [ if_(X.PropertyNotify, 'client') ])
act(focus_last_focused,          [ if_(X.DestroyNotify)    ])
act(install_colormap(),          [ if_(X.ColormapNotify)   ])
act(configure_request_handler(), [ if_(X.ConfigureRequest) ])
act(update_last_button_press,    [ if_(X.ButtonPress)      ])

act(viewport_absolute_move(  0,   0), [ if_key_press("u",      C+A) ])
act(viewport_absolute_move(  W,   0), [ if_key_press("i",      C+A) ])
act(viewport_absolute_move(W*2,   0), [ if_key_press("o",      C+A) ])
act(viewport_absolute_move(  0,   H), [ if_key_press("j",      C+A) ])
act(viewport_absolute_move(  W,   H), [ if_key_press("k",      C+A) ])
act(viewport_absolute_move(W*2,   H), [ if_key_press("l",      C+A) ])
act(viewport_absolute_move(  0, H*2), [ if_key_press("m",      C+A) ])
act(viewport_absolute_move(  W, H*2), [ if_key_press("comma",  C+A) ])
act(viewport_absolute_move(W*2, H*2), [ if_key_press("period", C+A) ])

act(viewport_relative_move(-W,  0),   [ if_key_press("Left",  C) ])
act(viewport_relative_move(+W,  0),   [ if_key_press("Right", C) ])
act(viewport_relative_move( 0, -H),   [ if_key_press("Up",    C) ])
act(viewport_relative_move( 0, +H),   [ if_key_press("Down",  C) ])

act(execute("aterm"), [ if_key_press("x", C+A) ])
act(execute("aterm"), [ if_root, if_button_press(1, Any), if_multiclick(2) ])

act(execute("sleep 1; xset s activate"), [ if_key_press("s", C+A) ])

def mpd(cmd):
    socksend('localhost', 6600, "%s\n" % cmd)

act(lambda ev: mpd("previous"), [ if_key_press("z", M4) ])
act(lambda ev: mpd("stop"),     [ if_key_press("x", M4) ])
act(lambda ev: mpd("play"),     [ if_key_press("c", M4) ])
act(lambda ev: mpd("pause"),    [ if_key_press("v", M4) ])
act(lambda ev: mpd("next"),     [ if_key_press("b", M4) ])

act(client_method("focus"),        [ if_client, if_button_press(1, Any, passthru=True) ])
act(delete_client(),               [ if_client, if_key_press('w', C+A) ])
act(start_move(),                  [ if_button_press(1, A), if_client ])
act(start_resize(),                [ if_button_press(3, A), if_client ])
act(client_method('stack_bottom'), [ if_button_press(4, A), if_client ])
act(client_method('stack_top'),    [ if_button_press(5, A), if_client ])

wm.register('event_done', event.smart_replay(),
    [ if_event_type(X.KeyPress, X.KeyRelease, X.ButtonPress, X.ButtonRelease) ]
)

infrastructure.run(wm)

