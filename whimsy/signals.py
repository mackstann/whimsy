# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import types

class publisher(object):
    def __init__(self, **defaults):
        self.signals = {}
        self.defaults = defaults

    def signal(self, name, **kw):
        kw_dict = dict(self.defaults, **kw)
        for func, filters in self.signals.get(name, [])[:]:
            for filt in filters:
                if not filt(**kw_dict):
                    break
            else:
                ret = func(**kw_dict)

    def register(self, mapping, callobj, *filters):
        if isinstance(mapping, types.DictType):
            for signalname, methodname in mapping.items():
                self.register(signalname, getattr(callobj, methodname), *filters)
            return

        signalname = mapping
        func = callobj
        self.signals[signalname] = self.signals.get(signalname, []) + [[func, filters]]

    def unregister(self, func):
        for sigset in self.signals.values():
            for actionset in sigset:
                if actionset[0] == func:
                    sigset.remove(actionset)

