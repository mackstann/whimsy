# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import logging, types

from whimsy import util

class return_code:
    DELETE_HANDLER = 0x10

class publisher:
    def __init__(self, **defaults):
        self.signals = {}
        self.defaults = defaults
        self.level = 0
        self.debug = False

    def signal(self, name, **kw):
        import time
        if self.debug:
            logging.debug(('    ' * self.level) + ('%0.3f' % time.time()) + ' <emitting ' + name + '>')
        self.level += 1
        sigdict = self.defaults.copy()
        sigdict.update(kw)
        sigdict['name'] = name
        signal = util.dict_to_object(sigdict)
        for func, filters in self.signals.get(name, [])[:]:
            for filt in filters:
                if not filt(signal):
                    break
            else:
                if self.debug:
                    logging.debug(('    ' * self.level) + ('%0.3f' % time.time()) + (' <executing %r' % func) + '>')
                self.level += 1
                ret = func(signal)
                if ret is not None:
                    if ret & return_code.DELETE_HANDLER:
                        self.signals[name].remove([func, filters])
                self.level -= 1
        self.level -= 1


    def register(self, mapping, callobj, *filters):
        if isinstance(mapping, types.DictType):
            for signalname, methodname in mapping.items():
                self.register(signalname, getattr(callobj, methodname), *filters)
            return

        signalname = mapping
        func = callobj
        self.signals[signalname] = self.signals.get(signalname, []) + [[func, filters]]

