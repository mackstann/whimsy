# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

class publisher(object):
    def __init__(self, **defaults):
        self.signals = {}
        self.defaults = defaults

    def emit(self, name, **kw):
        import time, sys
        if name != 'tick':
            print >>sys.stderr, time.time(), name, sorted(kw.keys())
        kw_dict = dict(self.defaults, **kw)
        for chain in self.signals.get(name, [])[:]:
            for func in chain:
                if not func(**kw_dict):
                    break

    def attach(self, name, *chain):
        self.signals.setdefault(name, []).append(chain)
        for f in chain: # HACK
            if hasattr(f, '__connected__'):
                f.__connected__(**self.defaults)

    def detach(self, func):
        for chains in self.signals.values():
            for i, chain in enumerate(chains):
                if func in chain:
                    chains.pop(i)

