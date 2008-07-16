# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy import main
from whimsy.actions import ewmh
from whimsy.actions.builtins import *
from whimsy.actions.transformers import *
from whimsy.actions.event_handling import *
from whimsy.actions.replay import *
from whimsy.filters.bindings import *
from whimsy.filters import *
from whimsy.x11.modifiers import modifier_mask, modifier_core

app = main.main()
dpy = app.dpy
hub = app.hub
wm = app.wm
xec = app.xec
ticker = app.ticker

modcore = modifier_core(dpy)

makemod = lambda raw_modifier: modifier_mask(modcore, raw_modifier)

Any = makemod(X.AnyModifier)

M1 = Mod1 = makemod(X.Mod1Mask)
M2 = Mod2 = makemod(X.Mod2Mask)
M3 = Mod3 = makemod(X.Mod3Mask)
M4 = Mod4 = makemod(X.Mod4Mask)
M5 = Mod5 = makemod(X.Mod5Mask)

S  = Shift   = makemod(X.ShiftMask)
C  = Control = makemod(X.ControlMask)

A = Alt = Mod1

Button1Mask = makemod(X.Button1Mask)
Button2Mask = makemod(X.Button2Mask)
Button3Mask = makemod(X.Button3Mask)
Button4Mask = makemod(X.Button4Mask)
Button5Mask = makemod(X.Button5Mask)
ButtonMask = Button1Mask+Button2Mask+Button3Mask+Button4Mask+Button5Mask

root_geometry = app.wm.root.get_geometry()
W = root_geometry.width
H = root_geometry.height

startup_shutdown_signal_methods = {
    'wm_manage_after': 'startup',
    'wm_shutdown_before': 'shutdown',
}

client_list_tracking_signal_methods = {
    'after_manage_window': 'add_window',
    'after_unmanage_window': 'remove_window',
    'wm_shutdown_before': 'shutdown',
}

client_stacking_tracking_signal_methods = \
    client_list_tracking_signal_methods.copy()
client_stacking_tracking_signal_methods['after_raise_window'] = 'raise_window'
client_stacking_tracking_signal_methods['after_lower_window'] = 'lower_window'

client_focus_tracking_signal_methods = {
    'after_focus_window': 'refresh',
    'wm_shutdown_before': 'shutdown',
}

viewport_tracking_signal_methods = {
    'wm_manage_after': 'startup',
    'after_viewport_move': 'refresh',
}

clicks = click_counter()

def if_doubleclick(**kw):
    return clicks.if_multi(2)(**kw)

actions = [
    (startup_shutdown_signal_methods, ewmh.net_supported()),
    (startup_shutdown_signal_methods, ewmh.net_supporting_wm_check()),
    (startup_shutdown_signal_methods, ewmh.net_number_of_desktops()),
    (startup_shutdown_signal_methods, ewmh.net_current_desktop()),
    (startup_shutdown_signal_methods, ewmh.net_desktop_names()),
    (startup_shutdown_signal_methods, ewmh.net_desktop_geometry()),
    (viewport_tracking_signal_methods, ewmh.net_desktop_viewport()),
    (client_list_tracking_signal_methods, ewmh.net_client_list()),
    (client_stacking_tracking_signal_methods, ewmh.net_client_list_stacking()),
    (client_focus_tracking_signal_methods, ewmh.net_active_window()),

    ('wm_manage_after', discover_existing_windows()),

    ('existing_window_discovered', lambda win, **kw: wm.manage_window(win),
     if_should_manage_existing_window),

    ('event', lambda win, **kw: wm.manage_window(win),
     if_(X.MapRequest, wintype="unmanaged"), if_should_manage_new_window),

    ('event', client_method('focus'), if_(X.MapRequest, wintype='client')),

    ('event', client_method('focus'),
     if_(X.EnterNotify, wintype='client'), if_state(~ButtonMask)),

    ('event', unmanage_window(), if_(X.DestroyNotify, wintype='client')),

    ('event', unmanage_window(), if_(X.UnmapNotify, wintype='client')),

    ('event', update_client_list_focus(), if_(X.FocusIn, wintype='client')),

    ('event', update_client_property(),
     if_(X.PropertyNotify, wintype='client')),

    ('event', focus_last_focused(), if_(X.DestroyNotify)),

    ('event', install_colormap(), if_(X.ColormapNotify)),

    ('event', configure_request_handler(), if_(X.ConfigureRequest)),

    ('event', clicks, if_(X.ButtonPress)),

    ('client_init_after', client_method('configure', border_width=0)),

    ('client_init_after', client_method('map_normal')),

    ('event_done', smart_replay(),
     if_event_type(X.KeyPress, X.KeyRelease, X.ButtonPress, X.ButtonRelease)),
]

for action in actions:
    app.hub.register(action[0], action[1], *action[2:])

