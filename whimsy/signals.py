# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import types

class publisher(object):
    def __init__(self, **defaults):
        self.signals = {}
        self.defaults = defaults

    def signal(self, name, **kw):
        import time
        if name != 'tick':
            print time.time(), name, sorted(kw.keys())
        kw_dict = dict(self.defaults, **kw)
        for func, filters in self.signals.get(name, [])[:]:
            for filt in filters:
                if not filt(**kw_dict):
                    break
            else:
                ret = func(**kw_dict)

    def register(self, mapping, callobj, *filters):
        if isinstance(mapping, types.DictType):
            for name, methodname in mapping.items():
                self.register_func(name, getattr(callobj, methodname), *filters)
        else:
            self.register_func(mapping, callobj, *filters)

    def register_func(self, name, func, *filters):
        self.signals.setdefault(name, []).append([func, filters])
        # HACK -- filters and actions should be made into the same thing
        for f in filters:
            if hasattr(f, '__connected__'):
                f.__connected__(**self.defaults)

    def unregister(self, func):
        for sigset in self.signals.values():
            for actionset in sigset:
                if actionset[0] == func:
                    sigset.remove(actionset)

