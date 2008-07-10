# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import unittest, traceback, sys
from Xlib import display, X
from whimsy.x11 import props

class TestPropertyInfo(unittest.TestCase):
    def setUp(self):
        self.dpy = display.Display()
        self.root = self.dpy.screen().root

    def tearDown(self):
        self.dpy.close()

    def test__NET_WM_NAME(self):
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_WM_NAME', 'this is the value')
        self.assertEqual(atom, self.dpy.get_atom('UTF8_STRING'))
        self.assertEqual(format, 8)
        self.assertEqual(value, u'this is the value')

    def test__NET_SUPPORTED(self):
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_SUPPORTED', [
            self.dpy.get_atom('_NET_WM_ACTION_MAXIMIZE_HORZ'),
            self.dpy.get_atom('_NET_WM_ACTION_MAXIMIZE_VERT'),
            self.dpy.get_atom('_NET_WM_ACTION_FULLSCREEN')
        ])
        self.assertEqual(atom, self.dpy.get_atom('ATOM'))
        self.assertEqual(format, 32)
        self.assertEqual(value, [
            self.dpy.get_atom('_NET_WM_ACTION_MAXIMIZE_HORZ'),
            self.dpy.get_atom('_NET_WM_ACTION_MAXIMIZE_VERT'),
            self.dpy.get_atom('_NET_WM_ACTION_FULLSCREEN')
        ])

    def test__NET_WM_PID(self):
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_WM_PID', 5)
        self.assertEqual(atom, self.dpy.get_atom('CARDINAL'))
        self.assertEqual(format, 32)
        self.assertEqual(value, [5])

    def test__NET_WM_STRUT(self):
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_WM_STRUT', [1, 2, 3, 4])
        self.assertEqual(atom, self.dpy.get_atom('CARDINAL'))
        self.assertEqual(format, 32)
        self.assertEqual(value, [1, 2, 3, 4])

    def test__NET_WM_STRUT_PARTIAL(self):
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_WM_STRUT_PARTIAL', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertEqual(atom, self.dpy.get_atom('CARDINAL'))
        self.assertEqual(format, 32)
        self.assertEqual(value, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        #testing multiples of 12 or not
        self.assertRaises(Exception, props.prepare_prop_for_write, self.dpy, '_NET_WM_STRUT_PARTIAL', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        self.assertRaises(Exception, props.prepare_prop_for_write, self.dpy, '_NET_WM_STRUT_PARTIAL', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

    def test__NET_ACTIVE_WINDOW(self):
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_ACTIVE_WINDOW', X.NONE)
        self.assertEqual(atom, self.dpy.get_atom('WINDOW'))
        self.assertEqual(format, 32)
        self.assertEqual(value, [X.NONE])

    def test__NET_DESKTOP_NAMES(self):
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_DESKTOP_NAMES', ["hey", "there", u"guy"])
        self.assertEqual(atom, self.dpy.get_atom('UTF8_STRING'))
        self.assertEqual(format, 8)
        self.assertEqual(value, ["hey", "there", u"guy"])

    def test__NET_CLIENT_LIST(self):
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_CLIENT_LIST', [X.NONE, self.dpy.screen().root.id])
        self.assertEqual(atom, self.dpy.get_atom('WINDOW'))
        self.assertEqual(format, 32)
        self.assertEqual(value, [X.NONE, self.dpy.screen().root.id])

    def test__NET_DESKTOP_VIEWPORT(self):
        viewport_origins_per_desktop = [
            1, 3,
            1, 2,
            1000, -1
        ]
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_DESKTOP_VIEWPORT', viewport_origins_per_desktop)
        self.assertEqual(atom, self.dpy.get_atom('CARDINAL'))
        self.assertEqual(format, 32)
        self.assertEqual(value, viewport_origins_per_desktop)

    def test__NET_WORKAREA(self):
        workarea_bounds_per_desktop = [
            1, 3, 4, 6,
            0, 1, 2, 900,
            3000000, 1000, -1, -800
        ]
        atom, format, value = props.prepare_prop_for_write(self.dpy, '_NET_WORKAREA', workarea_bounds_per_desktop)
        self.assertEqual(atom, self.dpy.get_atom('CARDINAL'))
        self.assertEqual(format, 32)
        self.assertEqual(value, workarea_bounds_per_desktop)

class TestChangeProp(unittest.TestCase):
    def setUp(self):
        self.dpy = display.Display()
        self.root = self.dpy.screen().root
        self.win = self.dpy.screen().root.create_window(0, 0, 10, 10, 0, X.CopyFromParent)

    def tearDown(self):
        self.win.destroy()
        self.dpy.close()

    def test_single_UTF8_STRING(self):
        props.change_prop(self.dpy, self.win, '_NET_WM_NAME', 'hey guy')
        val = props.get_prop(self.dpy, self.win, '_NET_WM_NAME')
        self.assertEqual(val, 'hey guy')

    def test_single_WINDOW(self):
        props.change_prop(self.dpy, self.root, '_NET_ACTIVE_WINDOW', X.NONE)
        val = props.get_prop(self.dpy, self.root, '_NET_ACTIVE_WINDOW')
        self.assertEqual(val, X.NONE)

        props.change_prop(self.dpy, self.root, '_NET_ACTIVE_WINDOW', self.win)
        val = props.get_prop(self.dpy, self.root, '_NET_ACTIVE_WINDOW')
        self.assertEqual(val, self.win.id)

if __name__ == '__main__':
    unittest.main()

