# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2006.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

from Xlib import X, XK, display
import sys

# modifiers: one of the 39580298 tricky things about X

class modifier_core(object):
    def __init__(self, dpy=display.Display()):
        self.dpy = dpy
        self.nlock = 0
        self.slock = 0
        self.setup_funnylocks()

    def setup_funnylocks(self):
        ks_to_kc = self.dpy.keysym_to_keycode
        nlock_key = ks_to_kc(XK.string_to_keysym("Num_Lock"))
        slock_key = ks_to_kc(XK.string_to_keysym("Scroll_Lock"))
        mapping = self.dpy.get_modifier_mapping()
        mod_names = "Shift Lock Control Mod1 Mod2 Mod3 Mod4 Mod5".split()
        if nlock_key and slock_key: # and?
            for modname in mod_names:
                index = getattr(X, "%sMapIndex" % modname)
                mask = getattr(X, "%sMask" % modname)
                if nlock_key and nlock_key in mapping[index]:
                    self.nlock = mask
                if slock_key and slock_key in mapping[index]:
                    self.slock = mask

    def get_all_modmasks(self, modmask):
        if modmask & X.AnyModifier:
            return (modmask,)
        return (modmask,
                modmask | self.nlock,
                modmask | self.slock,
                modmask | self.nlock | self.slock,
                modmask | X.LockMask,
                modmask | X.LockMask | self.nlock,
                modmask | X.LockMask | self.slock,
                modmask | X.LockMask | self.nlock | self.slock)

    def modmask_eq(self, lhs, rhs):
        if lhs & X.AnyModifier or rhs & X.AnyModifier:
            return True
        lhs &= ~(X.LockMask | self.nlock | self.slock)
        rhs &= ~(X.LockMask | self.nlock | self.slock)
        return lhs == rhs

    def modmask_and(self, lhs, rhs):
        if lhs & X.AnyModifier or rhs & X.AnyModifier:
            return rhs
        lhs &= ~(X.LockMask | self.nlock | self.slock)
        rhs &= ~(X.LockMask | self.nlock | self.slock)
        return lhs & rhs


class modifier_mask(object):
    def __init__(self, modcore, match=0, negate=0):
        self.modcore = modcore
        self.match = match
        self.negate = negate

    def __add__(self, rhs):
        return modifier_mask(self.modcore,
                ~rhs.negate & (self.match | rhs.match),
                ~rhs.match & (self.negate | rhs.negate))

    def __minus__(self, rhs):
        return modifier_mask(self.modcore,
                self.match | ~rhs.match, self.negate | rhs.match)

    def matches(self, modmask):
        return (self.modcore.modmask_and(modmask, self.match) == self.match and
                not self.modcore.modmask_and(modmask, self.negate))

