# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy import main
from whimsy.actions import ewmh
from whimsy.actions.builtins import *
from whimsy.actions.transformers import *
from whimsy.actions.event_handling import *
from whimsy.actions.flipping import *
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

ewmh.net_supported(hub, wm)
ewmh.net_supporting_wm_check(hub, wm)
ewmh.net_number_of_desktops(hub, wm)
ewmh.net_current_desktop(hub, wm)
ewmh.net_desktop_geometry(hub, wm)
ewmh.net_client_list(hub, wm)
ewmh.net_client_list_stacking(hub, wm)
ewmh.net_desktop_viewport(hub, wm)
ewmh.net_desktop_names(hub, wm)
ewmh.net_active_window(hub, wm)
ewmh.net_wm_strut_partial(hub, wm)

chains = [
    ('wm_manage_after', discover_existing_windows()),

    ('existing_window_discovered', if_should_manage_existing_window,
                                   lambda wm, win, **kw: wm.manage_window(win)),

    ('map_request', if_unmanaged,
                    if_should_manage_new_window,
                    lambda wm, win, **kw: wm.manage_window(win)),

    ('map_request',  if_client, client_method('focus')),
    ('enter_notify', if_client, client_method('focus')),

    #('enter_notify', if_root, lambda wm, **kw: wm.focus_root()),

    ('destroy_notify',  if_client, unmanage_window()),
    ('unmap_notify',    if_client, unmanage_window()),
    ('focus_in',        if_client, update_client_list_focus()),
    ('property_notify', if_client, update_client_property()),

    ('destroy_notify',    focus_last_focused()),
    ('colormap_notify',   install_colormap()),
    ('configure_request', configure_request_handler()), # rename this function

    ('client_init_after', client_method('configure', border_width=0)),
    ('client_init_after', client_method('map_normal')),
]

for chaininfo in chains:
    name = chaininfo[0]
    chain = chaininfo[1:]
    hub.attach(name, *chain)

