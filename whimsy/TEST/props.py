# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import traceback, sys
from Xlib import display, X
from whimsy import props

def TEST__change_property_argmaker():
    spec = props._window_props['_NET_WM_NAME']
    propinfo = props.property_info(dpy, spec)

    atom, format, value = propinfo.get('this is the value')
    assert atom == dpy.get_atom('UTF8_STRING')
    assert format == 8
    assert value == u'this is the value'

    spec = props._window_props['_NET_SUPPORTED']
    propinfo = props.property_info(dpy, spec)
    atom, format, value = propinfo.get([
        dpy.get_atom('_NET_WM_ACTION_MAXIMIZE_HORZ'),
        dpy.get_atom('_NET_WM_ACTION_MAXIMIZE_VERT'),
        dpy.get_atom('_NET_WM_ACTION_FULLSCREEN')
    ])
    assert atom == dpy.get_atom('ATOM')
    assert format == 32
    assert value == [
        dpy.get_atom('_NET_WM_ACTION_MAXIMIZE_HORZ'),
        dpy.get_atom('_NET_WM_ACTION_MAXIMIZE_VERT'),
        dpy.get_atom('_NET_WM_ACTION_FULLSCREEN')
    ]

    spec = props._window_props['_NET_WM_PID']
    propinfo = props.property_info(dpy, spec)
    atom, format, value = propinfo.get(5)
    assert atom == dpy.get_atom('CARDINAL')
    assert format == 32
    assert value == 5

    spec = props._window_props['_NET_WM_STRUT']
    propinfo = props.property_info(dpy, spec)
    atom, format, value = propinfo.get([1, 2, 3, 4])
    assert atom == dpy.get_atom('CARDINAL')
    assert format == 32
    assert value == [1, 2, 3, 4]

    spec = props._window_props['_NET_WM_STRUT_PARTIAL']
    propinfo = props.property_info(dpy, spec)
    atom, format, value = propinfo.get([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    assert atom == dpy.get_atom('CARDINAL')
    assert format == 32
    assert value == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    assert_exc(lambda: propinfo.get([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))
    assert_exc(lambda: propinfo.get([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]))

    spec = props._window_props['_NET_ACTIVE_WINDOW']
    propinfo = props.property_info(dpy, spec)
    atom, format, value = propinfo.get(X.NONE)
    assert atom == dpy.get_atom('WINDOW')
    assert format == 32
    assert value == [X.NONE]

    spec = props._window_props['_NET_DESKTOP_NAMES']
    propinfo = props.property_info(dpy, spec)
    atom, format, value = propinfo.get(["hey", "there", u"guy"])
    assert atom == dpy.get_atom('UTF8_STRING')
    assert format == 8
    assert value == ["hey", "there", u"guy"]

    spec = props._window_props['_NET_CLIENT_LIST']
    propinfo = props.property_info(dpy, spec)
    atom, format, value = propinfo.get([X.NONE, dpy.screen().root])
    assert atom == dpy.get_atom('WINDOW')
    assert format == 32
    assert value == [X.NONE, dpy.screen().root.id]

    spec = props._window_props['_NET_DESKTOP_VIEWPORT']
    propinfo = props.property_info(dpy, spec)
    al = [
        1, 3,
        1, 2,
        1000, -1
    ]
    atom, format, value = propinfo.get(al)
    assert atom == dpy.get_atom('CARDINAL')
    assert format == 32
    assert value == al

    spec = props._window_props['_NET_WORKAREA']
    propinfo = props.property_info(dpy, spec)
    al = [
        1, 3, 4, 6,
        0, 1, 2, 900,
        3000000, 1000, -1, -800
    ]
    atom, format, value = propinfo.get(al)
    assert atom == dpy.get_atom('CARDINAL')
    assert format == 32
    assert value == al

def TEST__change_prop():
    class x:pass
    wm = x()
    wm.dpy = dpy

    win = dpy.screen().root.create_window(0, 0, 1, 1, 0, X.CopyFromParent)

    props.change_prop(wm.dpy, win, '_NET_WM_NAME', 'hey guy')
    dpy.sync()
    val = props.get_prop(wm.dpy, win, '_NET_WM_NAME', 'UTF8_STRING')
    assert val == 'hey guy'

    props.change_prop(wm.dpy, root, '_NET_ACTIVE_WINDOW', X.NONE)
    dpy.sync()
    val = props.get_prop(wm.dpy, root, '_NET_ACTIVE_WINDOW', 'WINDOW')
    assert val == X.NONE

    # make interface for getting properties
    # for array-like things (list strings), return val.value.
    # for single values (window, cardinal), return val.value[0].

def _exception_class_name(c):
    if hasattr(c, '__name__'):
        return c.__name__
    name = str(c)
    if name.startswith('exceptions.'):
        return name.replace('exceptions.', '')
    return name

def assert_exc(func, exception_classes=()):
    exception_classes = tuple(exception_classes)
    msg = (
        "Expected %s to be raised, but %%s!" %
        ' or '.join([ _exception_class_name(c) for c in exception_classes ])
    )
    try:
        func()
    except exception_classes:
        return
    except:
        if exception_classes == ():
            return
        e = sys.exc_info()[1]
        raise AssertionError(
            msg % ("%s was raised instead" % _exception_class_name(e.__class__))
        )
    raise AssertionError(msg % "it wasn't")

dpy = display.Display()
root = dpy.screen().root

def get_test_func_names(filename):
    for line in open(filename):
        if line.startswith('def TEST__'):
            yield line.split(' ', 1)[1].split('(', 1)[0]

def run_test_func(func):
    try:
        print '    running %s...' % funcname,
        func()
    except Exception, e:
        print 'FAILED!'
        print
        s = traceback.format_exc()
        for line in s.split("\n"):
            print "        %s" % line
        print
    else:
        print 'passed!'

for funcname in get_test_func_names(__file__):
    run_test_func(globals()[funcname])

dpy = None
root = X.NONE

