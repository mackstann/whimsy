import types

from whimsy import util
from whimsy.log import *

class return_code:
    DELETE_HANDLER = 0x10
    SIGNAL_FINISHED = 0x20

    FINISHED_AND_DELETE = DELETE_HANDLER | SIGNAL_FINISHED

class publisher:
    def __init__(self, **defaults):
        self.signals = {}
        self.defaults = defaults

    def signal(self, name, **kw):
        sigdict = self.defaults.copy()
        sigdict.update(kw)
        sigdict['name'] = name
        signal = util.dict_to_object(sigdict)
        for func, filters in self.signals.get(name, [])[:]:
            for filt in filters:
                if not filt(signal):
                    break
            else:
                ret = func(signal)
                if ret is not None:
                    if ret & return_code.DELETE_HANDLER:
                        self.signals[name].remove([func, filters])
                    if ret & return_code.SIGNAL_FINISHED:
                        return


    def register_methods(self, mapping, callobj, filters=[]):
        for signame, methodname in mapping.items():
            self.register(signame, getattr(callobj, methodname), filters)

    def register(self, name, func, filters=[]):
        self.signals[name] = self.signals.get(name, []) + [[func, filters]]

