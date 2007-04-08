# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

import os, sys, signal, traceback, time

sys.path.insert(0, '.')

from Xlib.display import Display
from Xlib import X, XK
import select

from whimsy.log import *
from whimsy import event, modifiers, props, util
from whimsy.actions.builtins import *
from whimsy.actions.event_handling import *
from whimsy.client import managed_client
from whimsy import window_manager

import whimsy.ewmh.plugins
from whimsy import ewmh

import whimsy.infrastructure as main
from whimsy.infrastructure.modifiers import *

from whimsy.filters import *
from whimsy.filters.bindings import *

wm = main.init()

class wrap_xevent:
    def __call__(self, signal):
        t = time.time()
        signal.wm.signal('event_begin', ev=signal.xev)
        signal.wm.signal('event', ev=signal.xev)
        signal.wm.signal('event_done', ev=signal.xev)
        t2 = time.time()
        debug('took %0.2f ms to handle %s' % ((t2-t) * 1000, signal.xev.__class__.__name__))

wm.register('xevent', wrap_xevent())

rootgeom = wm.root.get_geometry()
W = rootgeom.width
H = rootgeom.height

# new concept: signal filters

wm.register({
        'wm_manage_after': 'startup',
        'wm_shutdown_before': 'shutdown',
    }, ewmh.plugins.net_supported()
)
wm.register({
        'wm_manage_after': 'startup',
        'wm_shutdown_before': 'shutdown',
    }, ewmh.plugins.net_supporting_wm_check()
)
wm.register({
        'wm_manage_after': 'startup',
        'wm_shutdown_before': 'shutdown',
    }, ewmh.plugins.net_desktop_geometry(width=W*3, height=H*3)
)
wm.register('wm_manage_after', ewmh.plugins.initialize_net_desktop_viewport())

#IDEA!!
# have the wm have 'states' or 'scenes' (in game terms)
# this would allow for clean move/resize loops
# have some handlers that persist in all new scenes (just a boolean called 'persist'?)

# make a convenience filter that combines ev type / win type

wm.register('event', manage_new_window_on_map_request(),          [ if_(X.MapRequest)  ])
wm.register('event', client_method('map_normal'),                 [ if_(X.MapRequest, 'client') ])

# how to focus root now?
wm.register('event', client_method('focus'),                      [ if_(X.MapRequest, 'client') ])

#use infrastructure.modifiers.ButtonMask.matches()
wm.register('event', client_method('focus'),                      [ if_(X.EnterNotify, 'client'), if_state(~ButtonMask) ])

wm.register('event', remove_client(),                             [ if_(X.DestroyNotify, 'client') ])

focus = focus_tracker()
wm.register('event', focus.record_focus_event,                    [ if_(X.FocusIn, 'client') ])
wm.register('event', focus.focus_last_focused,                    [ if_(X.DestroyNotify) ])

wm.register('event', install_colormap(),                          [ if_(X.ColormapNotify)   ])
wm.register('event', configure_request_handler(),                 [ if_(X.ConfigureRequest) ])
wm.register('event', update_client_property_on_property_notify(), [ if_(X.PropertyNotify, 'client') ])

wm.register('event', viewport_absolute_move(  0,   0),            [ if_key_press("u",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  W,   0),            [ if_key_press("i",      Control+Alt) ])
wm.register('event', viewport_absolute_move(W*2,   0),            [ if_key_press("o",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  0,   H),            [ if_key_press("j",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  W,   H),            [ if_key_press("k",      Control+Alt) ])
wm.register('event', viewport_absolute_move(W*2,   H),            [ if_key_press("l",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  0, H*2),            [ if_key_press("m",      Control+Alt) ])
wm.register('event', viewport_absolute_move(  W, H*2),            [ if_key_press("comma",  Control+Alt) ])
wm.register('event', viewport_absolute_move(W*2, H*2),            [ if_key_press("period", Control+Alt) ])

wm.register('event', viewport_relative_move(-W,  0),              [ if_key_press("Left",  Control) ])
wm.register('event', viewport_relative_move(+W,  0),              [ if_key_press("Right", Control) ])
wm.register('event', viewport_relative_move( 0, -H),              [ if_key_press("Up",    Control) ])
wm.register('event', viewport_relative_move( 0, +H),              [ if_key_press("Down",  Control) ])

wm.register('event', execute("aterm"),                            [ if_key_press("x", Control+Alt) ])

wm.register('event', execute("aterm"),                            [ if_root, if_button_press(1, Any, count=2) ])

wm.register('event', client_method("focus"),                      [ if_client, if_button_press(1, Any, passthru=True) ])

wm.register('event', client_method('stack_bottom'),               [ if_button_press(4, Alt ), if_client ])
wm.register('event', client_method('stack_top'),                  [ if_button_press(5, Alt ), if_client ])

wm.register('event', delete_client(),                             [ if_client, if_key_press('w', Control+Alt) ])

wm.register('event', start_move(),                                [ if_button_press(1, Alt ), if_client ])
wm.register('event', start_resize(),                              [ if_button_press(3, Alt ), if_client ])

wm.register('event_done', event.smart_replay())

#window.configure(stack_mode=X.Above)

def remove_client_border(signal):
    signal.client.border_size(0)
wm.register('client_init_before', remove_client_border)

main.run(wm, resolution=10)

