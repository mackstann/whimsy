# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, XK, display
import sys

class modifier_core(object):
    """caps lock, numlock, and scroll lock make comparing modifiers kind of
    hellish.  it's all contained here."""
    def __init__(self, dpy):
        self.dpy = dpy
        self.nlock = 0
        self.slock = 0
        self.setup_funnylocks()

    def setup_funnylocks(self):
        nlock_key = self.dpy.keysym_to_keycode(XK.string_to_keysym("Num_Lock"))
        slock_key = self.dpy.keysym_to_keycode(XK.string_to_keysym("Scroll_Lock"))
        mapping = self.dpy.get_modifier_mapping()
        mod_names = "Shift Lock Control Mod1 Mod2 Mod3 Mod4 Mod5".split()
        for modname in mod_names:
            index = getattr(X, "%sMapIndex" % modname)
            mask = getattr(X, "%sMask" % modname)
            if nlock_key and nlock_key in mapping[index]:
                self.nlock = mask
            if slock_key and slock_key in mapping[index]:
                self.slock = mask

    def every_lock_combination(self, mask):
        if mask & X.AnyModifier:
            return (X.AnyModifier,)
        clean = mask & ~(X.LockMask | self.nlock | self.slock)
        return (
            clean | X.LockMask,
            clean | X.LockMask | self.nlock,
            clean | X.LockMask | self.nlock | self.slock,
            clean | self.nlock,
            clean | self.nlock | self.slock,
            clean | self.slock,
        )

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
    def __init__(self, modcore, match=0):
        self.modcore = modcore
        self.match = match

    def __add__(self, rhs):
        return modifier_mask(self.modcore, self.match | rhs.match)

    def __invert__(self):
        return modifier_mask(self.modcore, self.negate, self.match)

    def matches(self, modmask):
        # no need for special modmask_and -- just &
        return self.modcore.modmask_and(modmask, self.match) == self.match

    def every_lock_combination(self):
        return self.modcore.every_lock_combination(self.match)
