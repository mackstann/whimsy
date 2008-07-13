# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import unittest
from whimsy.signals import publisher

class TestPassingSignalArgs(unittest.TestCase):
    def setUp(self):
        self.hub = publisher()

    def try_it_with_this_function(self, func):
        self.hub.register('event', func)
        self.hub.signal('event', a=1, b=2, c=3)

    def test_some_params_different_order(self):
        def func(a, c, **kw):
            self.assertEqual(a, 1)
            self.assertEqual(c, 3)
            self.assertEqual(kw, {'b':2})
        self.try_it_with_this_function(func)

    def test_some_params_same_order(self):
        def func(a, b, **kw):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(kw, {'c':3})
        self.try_it_with_this_function(func)

    def test_all_params_same_order(self):
        def func(a, b, c):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)
        self.try_it_with_this_function(func)

    def test_all_params_different_order(self):
        def func(b, c, a):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)
        self.try_it_with_this_function(func)

    def test_all_params_plus_starstar(self):
        def func(a, b, c, **kw):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)
            self.assertEqual(kw, {})
        self.try_it_with_this_function(func)

    def test_only_starstar(self):
        def func(**kw):
            self.assertEqual(kw, {'a':1, 'b':2, 'c':3})
        self.try_it_with_this_function(func)

    def test_not_enough_params(self):
        self.assertRaises(Exception, self.try_it_with_this_function, lambda a, b: None)

    def test_no_params(self):
        self.assertRaises(Exception, self.try_it_with_this_function, lambda: None)

    def test_only_star(self):
        self.assertRaises(Exception, self.try_it_with_this_function, lambda *args: None)

class TestDefaultsArePassedTheSameAsSignalKeywordArgs(unittest.TestCase):
    def setUp(self):
        self.hub = publisher(foo=1)

    def try_it_with_this_function(self, func):
        self.hub.register('event', func)
        self.hub.signal('event', bar=2)

    def test(self):
        def func(foo, bar):
            self.assertEqual(foo, 1)
            self.assertEqual(bar, 2)
        self.try_it_with_this_function(func)

    def test_defaults_dict_is_used_the_same_as_constructor_kwargs(self):
        self.hub.defaults['foo'] = 5
        def func(foo, bar):
            self.assertEqual(foo, 5)
            self.assertEqual(bar, 2)
        self.try_it_with_this_function(func)



if __name__ == '__main__':
    unittest.main()

