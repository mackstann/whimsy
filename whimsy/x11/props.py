# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xatom, protocol
from Xlib.xobject import drawable
import types

datatype_sizes = {
    'ATOM': 32,
    'CARDINAL': 32,
    'STRING': 8,
    'UTF8_STRING': 8,
    'WINDOW': 32,
}

class prop_definition(object):
    def __init__(self, type, aggregate_type='single', aggregate_size_multiple=1):
        self.type = type
        self.aggregate_type = aggregate_type
        self.aggregate_size_multiple = aggregate_size_multiple

    @property
    def format(self):
        return datatype_sizes[self.type]

    def validate(self, agg):
        if self.aggregate_type != 'array':
            self.validate_single_element(agg)
            return
        iter(agg)
        assert len(agg) % self.aggregate_size_multiple == 0
        for x in agg:
            self.validate_single_element(x)

    def validate_single_element(self, val):
        # unicode stuff is still seriously retarded
        if self.type == 'UTF8_STRING':
            assert val == unicode(val)
        elif self.type == 'STRING':
            assert val == str(val)
        elif self.type in ('ATOM', 'CARDINAL', 'WINDOW'):
            assert (
                isinstance(val, types.LongType) or isinstance(val, types.IntType)
                or (self.type == 'WINDOW' and isinstance(val, drawable.Window))
            )

    def convert(self, val):
        if self.aggregate_type == 'array':
            return [ self.convert_single_element(v) for v in val ]
        elif self.aggregate_type == 'nullarray':
            return [ self.convert_single_element(v) + '\0' for v in val ]
        elif self.format == 32:
            return [ self.convert_single_element(val) ]
        return self.convert_single_element(val)

    def convert_single_element(self, val):
        # doing change_prop(..., [ w.id for w in windows ]) gets real old, so
        # whereas python-xlib only takes numerical window ids for a WINDOW
        # property, we allow window objects to be passed in and we use the id
        # property of the objects automatically
        if self.type == 'WINDOW' and isinstance(val, drawable.Window):
            return val.id
        return val


all_props = {
    # client

    # WM_STATE is such a gross beast because it has its own type which contains
    # two items, each of a different type.  it is basically like a struct when
    # ALL of the other properties are like arrays or scalars.  so fuck it.
    # besides, python-xlib provides special getters/setters for these icccm
    # WM_* properties -- but the schism between that interface and this one is
    # worth avoiding, generally speaking.

    #"WM_STATE":                  prop_definition("WM_STATE"),
    "WM_NAME":                   prop_definition("STRING"),
    "WM_CLASS":                  prop_definition("STRING", "nullarray"),
    "WM_ICON_NAME":              prop_definition("STRING"),
    "WM_PROTOCOLS":              prop_definition("ATOM", "array"),

    "_NET_WM_NAME":              prop_definition("UTF8_STRING"),
    "_NET_WM_VISIBLE_NAME":      prop_definition("UTF8_STRING"),
    "_NET_WM_ICON_NAME":         prop_definition("UTF8_STRING"),
    "_NET_WM_VISIBLE_ICON_NAME": prop_definition("UTF8_STRING"),

    "_NET_WM_WINDOW_TYPE":       prop_definition("ATOM", "array"),
    "_NET_WM_STATE":             prop_definition("ATOM", "array"),
    "_NET_WM_ALLOWED_ACTIONS":   prop_definition("ATOM", "array"),

    "_NET_WM_DESKTOP":           prop_definition("CARDINAL"),
    "_NET_WM_PID":               prop_definition("CARDINAL"),
    "_NET_WM_USER_TIME":         prop_definition("CARDINAL"),

    "_NET_DESKTOP_GEOMETRY":     prop_definition("CARDINAL", "array", 2),
    "_NET_WM_ICON_GEOMETRY":     prop_definition("CARDINAL", "array", 4),
    "_NET_FRAME_EXTENTS":        prop_definition("CARDINAL", "array", 4),
    "_NET_WM_STRUT":             prop_definition("CARDINAL", "array", 4),
    "_NET_WM_STRUT_PARTIAL":     prop_definition("CARDINAL", "array", 12),

    "_NET_WM_ICON":              prop_definition("CARDINAL", "array"),

    # client and root

    "_NET_SUPPORTING_WM_CHECK":  prop_definition("WINDOW"),

    # root

    "_NET_NUMBER_OF_DESKTOPS":   prop_definition("CARDINAL"),
    "_NET_SHOWING_DESKTOP":      prop_definition("CARDINAL"),
    "_NET_CURRENT_DESKTOP":      prop_definition("CARDINAL"),

    "_NET_ACTIVE_WINDOW":        prop_definition("WINDOW"),

    "_NET_DESKTOP_NAMES":        prop_definition("UTF8_STRING", "array"),

    "_NET_SUPPORTED":            prop_definition("ATOM", "array"),

    "_NET_CLIENT_LIST":          prop_definition("WINDOW", "array"),
    "_NET_CLIENT_LIST_STACKING": prop_definition("WINDOW", "array"),
    "_NET_VIRTUAL_ROOTS":        prop_definition("WINDOW", "array"),

    "_NET_DESKTOP_VIEWPORT":     prop_definition("CARDINAL", "array", 2),
    "_NET_WORKAREA":             prop_definition("CARDINAL", "array", 4),

    "_NET_DESKTOP_LAYOUT":       prop_definition("CARDINAL", "array", 4),

    "_WHIMSY_CLIENT_LIST_FOCUS": prop_definition("WINDOW", "array"),

    "_WHIMSY_LAST_BUTTON_PRESS": prop_definition("CARDINAL", "array", 6),
    "_WHIMSY_MULTICLICK_COUNT":  prop_definition("CARDINAL"),

    # ewmh message atoms that are not also window props and thus left out here:
    # _NET_CLOSE_WINDOW
    # _NET_MOVERESIZE_WINDOW
    # _NET_WM_MOVERESIZE
    # _NET_RESTACK_WINDOW
    # _NET_REQUEST_FRAME_EXTENTS
    # _NET_WM_PING
    # _NET_WM_SYNC_REQUEST

    # not here for other reasons:
    # _NET_WM_HANDLED_ICONS -- under-specified and icons are mostly obsolete
}

def supported_props():
    return all_props.keys()

def send_window_message(dpy, win, name, data,
        ev_win=X.NONE,
        event_mask=X.SubstructureNotifyMask|X.SubstructureRedirectMask):

    format = all_props[name].format

    data += [0] * (160/format - len(data))
    win.send_event(
        protocol.event.ClientMessage(
            window = ev_win,
            client_type = dpy.get_atom(name),
            data = (format, data),
        ),
        event_mask=event_mask
    )

def prepare_prop_for_write(dpy, name, value):
    definition = all_props[name]
    definition.validate(value)
    return (
        dpy.get_atom(definition.type),
        definition.format,
        definition.convert(value)
    )

def change_prop(dpy, win, name, value):
    type, format, processed_val = prepare_prop_for_write(dpy, name, value)
    win.change_property(dpy.get_atom(name), int(type), format, processed_val)

def get_prop(dpy, win, name):
    definition = all_props[name]
    prop = win.get_full_property(dpy.get_atom(name), dpy.get_atom(definition.type))

    if prop is None:
        return None if definition.aggregate_type == 'single' else []

    if definition.aggregate_type == 'array':
        return list(prop.value)

    if definition.aggregate_type == 'nullarray':
        return prop.value.split('\0')[:-1]

    if definition.format == 32:
        return prop.value[0] if len(prop.value) else None

    return prop.value

def delete_prop(dpy, win, name):
    win.delete_property(dpy.get_atom(name))

