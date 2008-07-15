# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import unittest
from whimsy.x11.size_hints import size_hints

class fake_raw_size_hints(object):
    flags = 0xffffffff
    def __init__(self, **kw):
        for k in kw:
            setattr(self, k, kw[k])

        class aspect: pass
        for attr in 'min_aspect', 'max_aspect':
            if attr in kw:
                setattr(self, attr, aspect())
                getattr(self, attr).num = kw[attr]
                getattr(self, attr).denum = 1


class TestYadda(unittest.TestCase):
    #def test_blah(self):
    #    raw = fake_raw_size_hints(
    #        base_width = 0,
    #        base_height = 0,
    #        min_aspect = 4/3.0,
    #        max_aspect = 4/3.0,
    #    )
    #    sh = size_hints(hints=raw)
    #    self.assertEqual(4096*75, 640*480)
    #    self.assertEqual(sh.fix_aspect(4096, 75), (640, 480))

    def test_change_to_aspect(self):
        sh = size_hints(hints=None)
        self.assertEqual(sh.change_to_aspect(1.0, 40, 90), (60, 60))
        self.assertEqual(sh.change_to_aspect(1.0, 90, 40), (60, 60))

if __name__ == '__main__':
    unittest.main()

