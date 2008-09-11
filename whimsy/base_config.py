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

ewmh.net_supported(hub)
ewmh.net_supporting_wm_check(hub)
ewmh.net_number_of_desktops(hub)
ewmh.net_current_desktop(hub)
ewmh.net_desktop_geometry(hub)
ewmh.net_client_list(hub)
ewmh.net_desktop_viewport(hub)

clicks = click_counter()

#replayer = smart_replay()

def if_doubleclick(**kw):
    return clicks.if_multi(2)(**kw)

actions = [
    ('wm_manage_after', discover_existing_windows()),

    ('existing_window_discovered', lambda wm, win, **kw: wm.manage_window(win),
     if_should_manage_existing_window),

    ('event', lambda wm, win, **kw: wm.manage_window(win),
     if_(X.MapRequest, wintype="unmanaged"), if_should_manage_new_window),

    ('event', client_method('focus'), if_(X.MapRequest, wintype='client')),

    ('event', client_method('focus'),
     if_(X.EnterNotify, wintype='client'), if_state(~ButtonMask)),

    ('event', lambda wm, **kw:
        wm.dpy.set_input_focus(wm.root, X.RevertToPointerRoot, X.CurrentTime),
     if_(X.EnterNotify, wintype='root'), if_state(~ButtonMask)),

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

    #('swallow_this_event', replayer.mark_current_event_for_swallowing),

    #('event_done', replayer,
    # if_event_type(X.KeyPress, X.KeyRelease, X.ButtonPress, X.ButtonRelease)),
]

for action in actions:
    app.hub.register(action[0], action[1], *action[2:])

