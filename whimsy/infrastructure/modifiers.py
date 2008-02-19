# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X

from whimsy.modifiers import (
    modifier_mask as _mask,
    modifier_core as _mc,
)

_m = _mc()

Any = _mask(_m, X.AnyModifier)

M1 = Mod1 = _mask(_m, X.Mod1Mask)
M2 = Mod2 = _mask(_m, X.Mod2Mask)
M3 = Mod3 = _mask(_m, X.Mod3Mask)
M4 = Mod4 = _mask(_m, X.Mod4Mask)
M5 = Mod5 = _mask(_m, X.Mod5Mask)

S  = Shift   = _mask(_m, X.ShiftMask)
C  = Control = _mask(_m, X.ControlMask)

A = Alt = Mod1

Button1Mask = _mask(_m, X.Button1Mask)
Button2Mask = _mask(_m, X.Button2Mask)
Button3Mask = _mask(_m, X.Button3Mask)
Button4Mask = _mask(_m, X.Button4Mask)
Button5Mask = _mask(_m, X.Button5Mask)
ButtonMask = Button1Mask+Button2Mask+Button3Mask+Button4Mask+Button5Mask

