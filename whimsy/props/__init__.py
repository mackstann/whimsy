# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2006.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from Xlib.display import Display
from Xlib import X, XK, error, Xutil, protocol, Xatom
import types

from whimsy.log import *
from whimsy import util

# single
# array
# arrayN

# cardinal
# utf8
# atom
# window
# string

_window_props = {
    # client
    "WM_STATE":                  [ "CARDINAL"                 ],
    "WM_NAME":                   [ "UTF8_STRING"              ],
    "WM_CLASS":                  [ "UTF8_STRING", "array"     ], # NONE OF THESE NEEDED..?
    "WM_ICON_NAME":              [ "UTF8_STRING"              ],
    "WM_PROTOCOLS":              [ "ATOM",        "array"     ],

    "_NET_WM_NAME":              [ "UTF8_STRING"              ],
    "_NET_WM_VISIBLE_NAME":      [ "UTF8_STRING"              ],
    "_NET_WM_ICON_NAME":         [ "UTF8_STRING"              ],
    "_NET_WM_VISIBLE_ICON_NAME": [ "UTF8_STRING"              ],

    "_NET_WM_WINDOW_TYPE":       [ "ATOM",        "array"     ],
    "_NET_WM_STATE":             [ "ATOM",        "array"     ],
    "_NET_WM_ALLOWED_ACTIONS":   [ "ATOM",        "array"     ],

    "_NET_WM_DESKTOP":           [ "CARDINAL"                 ],
    "_NET_WM_PID":               [ "CARDINAL"                 ],
    "_NET_WM_USER_TIME":         [ "CARDINAL"                 ],

    "_NET_DESKTOP_GEOMETRY":     [ "CARDINAL",    "array",  2 ],
    "_NET_WM_ICON_GEOMETRY":     [ "CARDINAL",    "array",  4 ],
    "_NET_FRAME_EXTENTS":        [ "CARDINAL",    "array",  4 ],
    "_NET_WM_STRUT":             [ "CARDINAL",    "array",  4 ],
    "_NET_WM_STRUT_PARTIAL":     [ "CARDINAL",    "array", 12 ],

    # client and root
    "_NET_SUPPORTING_WM_CHECK":  [ "WINDOW"                   ],

    # root
    "_NET_NUMBER_OF_DESKTOPS":   [ "CARDINAL"                 ],
    "_NET_SHOWING_DESKTOP":      [ "CARDINAL"                 ],
    "_NET_CURRENT_DESKTOP":      [ "CARDINAL"                 ],

    "_NET_ACTIVE_WINDOW":        [ "WINDOW"                   ],

    "_NET_DESKTOP_NAMES":        [ "UTF8_STRING", "array"     ],

    "_NET_SUPPORTED":            [ "ATOM",        "array"     ],

    "_NET_CLIENT_LIST":          [ "WINDOW",      "array"     ],
    "_NET_CLIENT_LIST_STACKING": [ "WINDOW",      "array"     ],
    "_NET_VIRTUAL_ROOTS":        [ "WINDOW",      "array"     ],

    "_NET_DESKTOP_VIEWPORT":     [ "CARDINAL",    "array",  2 ],
    "_NET_WORKAREA":             [ "CARDINAL",    "array",  4 ],

    "_NET_DESKTOP_LAYOUT":       [ "CARDINAL",    "array",  4 ],

    "_WHIMSY_CLIENT_LIST_FOCUS": [ "WINDOW",      "array",    ],

    "_WHIMSY_LAST_BUTTON_PRESS": [ "CARDINAL",    "array",  6 ],
    "_WHIMSY_MULTICLICK_COUNT":  [ "CARDINAL",                ],
}

def supported_props():
    return _window_props.keys()

def send_window_message(dpy, win, name, data,
        ev_win=X.NONE,
        event_mask=X.SubstructureNotifyMask|X.SubstructureRedirectMask):

    format = property_info.datatype_sizes[_window_props[name][0]]

    data += [0] * (160/format - len(data))
    win.send_event(
        protocol.event.ClientMessage(
            window = ev_win,
            client_type = dpy.get_atom(name),
            data = (format, data),
        ),
        event_mask=event_mask
    )

class property_info:
    def __init__(self, dpy, prop_spec):
        self.dpy = dpy
        self.spec = prop_spec

    def get(self, args):
        self.verify(args)
        return self.get_property_info(args)

    def verify_single(self, val):
        datatype = self.spec[0]
        if datatype == 'UTF8_STRING':
            assert val == unicode(val)
        elif datatype == 'STRING':
            assert val == str(val)
        elif datatype in ('ATOM', 'CARDINAL', 'WINDOW'):
            assert isinstance(val, types.LongType) or isinstance(val, types.IntType)

    def verify(self, agg):
        if len(self.spec) > 1:
            aggtype = self.spec[1]
            if aggtype == 'array':
                assert isinstance(agg, types.ListType) or isinstance(agg, types.TupleType)
                if len(self.spec) > 2:
                    assert len(agg) % self.spec[2] == 0
                for x in agg:
                    self.verify_single(x)
        else:
            self.verify_single(agg)

    datatype_sizes = {
        'UTF8_STRING': 8,
        'STRING': 8,
        'ATOM': 32,
        'CARDINAL': 32,
        'WINDOW': 32,
    }

    def convert_single(self, val):
        if self.spec[0] == 'WINDOW':
            if val != X.NONE:
                if hasattr(val, 'id'):
                    return val.id
                return val
        return val

    def convert_for_write(self, val):
        if len(self.spec) > 1:
            aggtype = self.spec[1]
            if aggtype == 'array':
                return [ self.convert_single(v) for v in val ]
        else:
            if self.datatype_sizes[self.spec[-1]] == 32:
                return [ self.convert_single(val) ]
            return self.convert_single(val)


    def get_property_info(self, val):
        self.verify(val)
        from Xlib import Xatom
        atomname = self.spec[0]
        if atomname in vars(Xatom):
            atom = getattr(Xatom, atomname)
        else:
            atom = self.dpy.get_atom(atomname)
        return (
            atom,
            self.datatype_sizes[self.spec[0]],
            self.convert_for_write(val),
        )

def change_prop(dpy, win, name, value):
    propinfo = property_info(dpy, _window_props[name])
    type, format, processed_val = propinfo.get(value)
    win.change_property(dpy.get_atom(name), int(type), format, processed_val)

def get_prop(dpy, win, name, type_name=None):
    spec = _window_props[name]
    prop = win.get_full_property(dpy.get_atom(name), dpy.get_atom(spec[0]))

    is_array_type = len(spec) > 1 and spec[1] == 'array'

    if prop is None:
        if is_array_type:
            return []
        return None

    if is_array_type:
        return list(prop.value)
    if property_info.datatype_sizes[spec[0]] == 32:
        assert len(prop.value) in (0, 1)
        if not len(prop.value):
            return None
        return prop.value[0]
    return prop.value

