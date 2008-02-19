# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, sys, signal, time

sys.path.insert(0, '.')

from Xlib import X

from whimsy import event, modifiers, props, util, infrastructure, window_manager
from whimsy.actions import ewmh

from whimsy.log import *
from whimsy.actions.builtins import *
from whimsy.actions.event_handling import *
from whimsy.infrastructure.modifiers import *
from whimsy.filters import *
from whimsy.filters.bindings import *

wm = infrastructure.init()

root_geometry = wm.root.get_geometry()
W = root_geometry.width
H = root_geometry.height

class wrap_xevent:
    def __call__(self, signal):
        t = time.time()
        signal.wm.signal('event_begin', ev=signal.xev)
        signal.wm.signal('event',       ev=signal.xev)
        signal.wm.signal('event_done',  ev=signal.xev)
        t2 = time.time()
        debug('took %0.2f ms to handle %s' % ((t2-t) * 1000, signal.xev.__class__.__name__))

# raw x events come in on the 'xevent' signal
wm.register('xevent', wrap_xevent())

startup_shutdown_signal_methods = {
    'wm_manage_after': 'startup',
    'wm_shutdown_before': 'shutdown',
}

wm.register_methods(startup_shutdown_signal_methods, ewmh.net_supported())
wm.register_methods(startup_shutdown_signal_methods, ewmh.net_supporting_wm_check())
wm.register_methods(startup_shutdown_signal_methods, ewmh.net_number_of_desktops())
wm.register_methods(startup_shutdown_signal_methods, ewmh.net_current_desktop())
wm.register_methods(startup_shutdown_signal_methods, ewmh.net_desktop_geometry(width=W*3, height=H*3))

wm.register_methods({
    'after_manage_window': 'refresh',
    'after_remove_client': 'refresh',
    'after_delete_client': 'refresh',
    'wm_shutdown_before': 'delete',
}, ewmh.net_client_list())

wm.register('wm_manage_after', ewmh.initialize_net_desktop_viewport())

#IDEA!!
# have the wm have 'states' or 'scenes' (in game terms)
# this would allow for clean move/resize loops
# have some handlers that persist in all new scenes (just a boolean called 'persist'?)

# perhaps somehow split actions up into <which window(s)> and <what to do
# to it/them>

# perhaps clean up variations between functions and callable instances -- the
# randomness of parentheses is confusing

# this will fix the border thing, allowing it to become before manage.

wm.register('wm_manage_after',            discover_existing_windows)
wm.register('existing_window_discovered', manage_window, [ if_should_manage_existing_window ])
wm.register('event',                      manage_window, [ if_(X.MapRequest), if_should_manage_new_window ])

wm.register('client_init_after', client_method('configure', border_width=0))
wm.register('client_init_after', client_method('map_normal'))

# how to focus root now?

wm.register('event', client_method('focus'),      [ if_(X.MapRequest,     'client') ])
wm.register('event', client_method('focus'),      [ if_(X.EnterNotify,    'client'), if_state(~ButtonMask) ]) #use infrastructure.modifiers.ButtonMask.matches()
wm.register('event', remove_client(),             [ if_(X.DestroyNotify,  'client') ])
wm.register('event', remove_client(),             [ if_(X.UnmapNotify,    'client') ])
wm.register('event', update_client_list_focus,    [ if_(X.FocusIn,        'client') ])
wm.register('event', update_client_property(),    [ if_(X.PropertyNotify, 'client') ])
wm.register('event', focus_last_focused,          [ if_(X.DestroyNotify)    ])
wm.register('event', install_colormap(),          [ if_(X.ColormapNotify)   ])
wm.register('event', configure_request_handler(), [ if_(X.ConfigureRequest) ])
wm.register('event', update_last_button_press,    [ if_(X.ButtonPress)      ])

wm.register('event', viewport_absolute_move(  0,   0), [ if_key_press("u",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  W,   0), [ if_key_press("i",      Control+Alt) ])
wm.register('event', viewport_absolute_move(W*2,   0), [ if_key_press("o",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  0,   H), [ if_key_press("j",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  W,   H), [ if_key_press("k",      Control+Alt) ])
wm.register('event', viewport_absolute_move(W*2,   H), [ if_key_press("l",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  0, H*2), [ if_key_press("m",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  W, H*2), [ if_key_press("comma",  Control+Alt) ])
wm.register('event', viewport_absolute_move(W*2, H*2), [ if_key_press("period", Control+Alt) ])

wm.register('event', viewport_relative_move(-W,  0),   [ if_key_press("Left",  Control) ])
wm.register('event', viewport_relative_move(+W,  0),   [ if_key_press("Right", Control) ])
wm.register('event', viewport_relative_move( 0, -H),   [ if_key_press("Up",    Control) ])
wm.register('event', viewport_relative_move( 0, +H),   [ if_key_press("Down",  Control) ])

wm.register('event', execute("aterm"),                    [ if_key_press("x", Control+Alt) ])
wm.register('event', execute("sleep 1; xset s activate"), [ if_key_press("s", Control+Alt) ])

def socksend(host, port, text):
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(text)
        s.close()
    except socket.error:
        pass

def mpd(cmd):
    socksend('localhost', 6600, "%s\n" % cmd)

wm.register('event', lambda ev: mpd("previous"), [ if_key_press("z", Mod4) ])
wm.register('event', lambda ev: mpd("stop"),     [ if_key_press("x", Mod4) ])
wm.register('event', lambda ev: mpd("play"),     [ if_key_press("c", Mod4) ])
wm.register('event', lambda ev: mpd("pause"),    [ if_key_press("v", Mod4) ])
wm.register('event', lambda ev: mpd("next"),     [ if_key_press("b", Mod4) ])

#wm.register('event', client_method("moveresize", x, x, x, x), [
    #if_event_type(X.MapRequest),
    #if_client,
    #if_wm_class("Gecko", "Firefox-bin"),
    #if_wm_name("(.* \\- )?Mozilla Firefox"),
    # transient for
    #lambda s: s.ev.window.geom['width'] > 300
#])

wm.register('event', execute("aterm"),              [ if_root, if_button_press(1, Any), if_multiclick(2) ])
wm.register('event', client_method("focus"),        [ if_client, if_button_press(1, Any, passthru=True) ])
wm.register('event', delete_client(),               [ if_client, if_key_press('w', Control+Alt) ])
wm.register('event', start_move(),                  [ if_button_press(1, Alt), if_client ])
wm.register('event', start_resize(),                [ if_button_press(3, Alt), if_client ])
wm.register('event', client_method('stack_bottom'), [ if_button_press(4, Alt), if_client ])
wm.register('event', client_method('stack_top'),    [ if_button_press(5, Alt), if_client ])

wm.register('event_done', event.smart_replay(),
    [ if_event_type(X.KeyPress, X.KeyRelease, X.ButtonPress, X.ButtonRelease) ]
)

infrastructure.run(wm, resolution=10)

