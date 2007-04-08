# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2006.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

# XXX i don't like this anymore

class dictobj(dict):
    '''
    a wrapper around the standard python dictionary to allow .foo notation in
    addition to the dict's normal ['foo'] notation
    '''

    def __getattr__(self, name):
        return self[name]
    def __setattr__(self, name, value):
        self[name] = value

    def fromobj(obj, *attrs):
        '''
        usage: dictobj.fromobj(foo, 'attr1name', 'attr2name', ...)
        returns: dictobj with specified attrs copied from foo
        '''
        d = dictobj()
        for attr in attrs:
            d[attr] = getattr(obj, attr)
        return d
    fromobj = staticmethod(fromobj)

