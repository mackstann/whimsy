# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xatom
import types

_window_props = {
    # client
    "WM_STATE":                  [ "CARDINAL",    "single",    1, ],
    "WM_NAME":                   [ "STRING",      "single",    1, ],
    "WM_CLASS":                  [ "STRING",      "nullarray", 1, ],
    "WM_ICON_NAME":              [ "STRING",      "single",    1, ],
    "WM_PROTOCOLS":              [ "ATOM",        "array",     1, ],

    "_NET_WM_NAME":              [ "UTF8_STRING", "single",    1, ],
    "_NET_WM_VISIBLE_NAME":      [ "UTF8_STRING", "single",    1, ],
    "_NET_WM_ICON_NAME":         [ "UTF8_STRING", "single",    1, ],
    "_NET_WM_VISIBLE_ICON_NAME": [ "UTF8_STRING", "single",    1, ],

    "_NET_WM_WINDOW_TYPE":       [ "ATOM",        "array",     1, ],
    "_NET_WM_STATE":             [ "ATOM",        "array",     1, ],
    "_NET_WM_ALLOWED_ACTIONS":   [ "ATOM",        "array",     1, ],

    "_NET_WM_DESKTOP":           [ "CARDINAL",    "single",    1, ],
    "_NET_WM_PID":               [ "CARDINAL",    "single",    1, ],
    "_NET_WM_USER_TIME":         [ "CARDINAL",    "single",    1, ],

    "_NET_DESKTOP_GEOMETRY":     [ "CARDINAL",    "array",     2, ],
    "_NET_WM_ICON_GEOMETRY":     [ "CARDINAL",    "array",     4, ],
    "_NET_FRAME_EXTENTS":        [ "CARDINAL",    "array",     4, ],
    "_NET_WM_STRUT":             [ "CARDINAL",    "array",     4, ],
    "_NET_WM_STRUT_PARTIAL":     [ "CARDINAL",    "array",    12, ],

    # client and root
    "_NET_SUPPORTING_WM_CHECK":  [ "WINDOW",      "single",    1, ],

    # root
    "_NET_NUMBER_OF_DESKTOPS":   [ "CARDINAL",    "single",    1, ],
    "_NET_SHOWING_DESKTOP":      [ "CARDINAL",    "single",    1, ],
    "_NET_CURRENT_DESKTOP":      [ "CARDINAL",    "single",    1, ],

    "_NET_ACTIVE_WINDOW":        [ "WINDOW",      "single",    1, ],

    "_NET_DESKTOP_NAMES":        [ "UTF8_STRING", "array",     1, ],

    "_NET_SUPPORTED":            [ "ATOM",        "array",     1, ],

    "_NET_CLIENT_LIST":          [ "WINDOW",      "array",     1, ],
    "_NET_CLIENT_LIST_STACKING": [ "WINDOW",      "array",     1, ],
    "_NET_VIRTUAL_ROOTS":        [ "WINDOW",      "array",     1, ],

    "_NET_DESKTOP_VIEWPORT":     [ "CARDINAL",    "array",     2, ],
    "_NET_WORKAREA":             [ "CARDINAL",    "array",     4, ],

    "_NET_DESKTOP_LAYOUT":       [ "CARDINAL",    "array",     4, ],

    "_WHIMSY_CLIENT_LIST_FOCUS": [ "WINDOW",      "array",     1, ],

    "_WHIMSY_LAST_BUTTON_PRESS": [ "CARDINAL",    "array",     6 ],
    "_WHIMSY_MULTICLICK_COUNT":  [ "CARDINAL",    "single",    1, ],
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
        if self.spec[1] == 'array':
            assert isinstance(agg, types.ListType) or isinstance(agg, types.TupleType)
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
        if self.spec[1] == 'array':
            return [ self.convert_single(v) for v in val ]
        elif self.spec[1] == 'nullarray':
            return [ self.convert_single(v) + '\0' for v in val ]
        else:
            if self.datatype_sizes[self.spec[0]] == 32:
                return [ self.convert_single(val) ]
            return self.convert_single(val)


    def get_property_info(self, val):
        self.verify(val)
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

    if prop is None:
        return None if spec[1] == 'single' else []

    if spec[1] == 'array':
        return list(prop.value)

    if spec[1] == 'nullarray':
        return prop.value.split('\0')[:-1]

    if property_info.datatype_sizes[spec[0]] == 32:
        assert len(prop.value) in (0, 1)
        if not len(prop.value):
            return None
        return prop.value[0]
    return prop.value

def delete_prop(dpy, win, name):
    win.delete_property(dpy.get_atom(name))

