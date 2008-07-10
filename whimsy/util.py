# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X, Xutil
import sys, select, errno, socket

class size_hints(object):
    def __init__(self, **kw):
        if 'hints' in kw and 'win' not in kw:
            self.hints = kw["hints"]
        elif 'win' in kw:
            self.hints = kw["win"].get_wm_normal_hints()
        else:
            raise ValueError("pass either a 'win' or 'hints' argument, "
                             "but not both")

    def __get(self, attr, flag, lowerbound, default):
        if self.hints and self.hints.flags & flag:
            return max(getattr(self.hints, attr), lowerbound)
        return default

    def __get_aspect(self, attr):
        if self.hints and self.hints.flags & Xutil.PAspect:
            aspect = getattr(self.hints, attr)
            if aspect.num and aspect.denum:
                return float(aspect.num) / aspect.denum
        return 0

    base_width  = property(lambda self: self.__get("base_width",  Xutil.PBaseSize, 0, 0))
    base_height = property(lambda self: self.__get("base_height", Xutil.PBaseSize, 0, 0))
    min_width   = property(lambda self: self.__get("min_width",  Xutil.PMinSize, 0, 0))
    min_height  = property(lambda self: self.__get("min_height", Xutil.PMinSize, 0, 0))
    max_width   = property(lambda self: self.__get("max_width",  Xutil.PMaxSize, 0, sys.maxint))
    max_height  = property(lambda self: self.__get("max_height", Xutil.PMaxSize, 0, sys.maxint))
    width_inc   = property(lambda self: self.__get("width_inc",  Xutil.PResizeInc, 1, 1))
    height_inc  = property(lambda self: self.__get("height_inc", Xutil.PResizeInc, 1, 1))
    min_aspect  = property(lambda self: self.__get_aspect("min_aspect"))
    max_aspect  = property(lambda self: self.__get_aspect("max_aspect"))

    # "human" height/width means that it takes increments into account, i.e.
    # 80x25 for a terminal

    def get_human_width(self, width):
        return (width - self.base_width) / self.width_inc

    def get_human_height(self, height):
        return (height - self.base_height) / self.height_inc

    def get_gravity(self, default):
        if self.hints and self.hints.flags & Xutil.PWinGravity:
            return self.hints.win_gravity
        return default

    # from icccm: "If a base size is not provided, the minimum size is to be
    # used in its place and vice versa."

    def fix_increments(self, width, height):
        if self.hints and self.hints.flags & Xutil.PBaseSize:
            basew, baseh = self.base_width, self.base_height
        else:
            basew, baseh = self.min_width, self.min_height

        w, h = (width - (width - basew) % self.width_inc,
                height - (height - baseh) % self.height_inc)
        return w, h
            
    def fix_max(self, width, height):
        w, h = (min(width, self.max_width), min(height, self.max_height))
        return w, h

    def fix_min(self, width, height):
        if self.hints and self.hints.flags & Xutil.PMinSize:
            minw, minh = self.min_width, self.min_height
        else:
            minw, minh = self.base_width, self.base_height
        w, h = (max(width, minw), max(height, minh))
        return w, h

    def fix_aspect(self, width, height):
        w, h = max(width, 1), max(height, 1)
        if w == self.base_width and h == self.base_height:
            return w, h

        # this could very well be stupid
        try:
            aspect = float(w - self.base_width) / (h - self.base_height)
        except ZeroDivisionError:
            aspect = 1.0

        minaspect, maxaspect = self.min_aspect, self.max_aspect

        if minaspect > maxaspect:
            warning('minaspect is larger than maxaspect!')

        # only one of these two should happen, but in case they step on each
        # other, we will err on the side of a more wide/short aspect ratio

        if maxaspect and aspect > maxaspect:
            w, h = self.change_to_aspect(maxaspect, w, h)

        if minaspect and aspect < minaspect:
            w, h = self.change_to_aspect(minaspect, w, h)

        return w, h

    def change_to_aspect(self, aspect, width, height):
        # but retain same area
        h = int(round(float(width + height) / (aspect + 1)))
        w = int(round(h * aspect))
        return w, h


def configure_request_changes(ev):
    changes = {}
    if ev.value_mask & X.CWX: changes["x"] = ev.x
    if ev.value_mask & X.CWY: changes["y"] = ev.y
    if ev.value_mask & X.CWWidth: changes["width"] = ev.width
    if ev.value_mask & X.CWHeight: changes["height"] = ev.height
    if ev.value_mask & X.CWSibling: changes["sibling"] = ev.above
    if ev.value_mask & X.CWStackMode:
        changes["stack_mode"] = ev.stack_mode
    return changes

def window_type(wm, window):
    if window == wm.root:
        return "root"
    elif wm.window_to_client(window):
        return "client"
    return "unmanaged"

def socksend(host, port, text):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(text)
        s.close()
    except socket.error:
        pass

def lenient_select(r, w, x, timeout):
    # sigchld for example will interrupt select() and cause an unhandled
    # socket.error exception.
    try:
        return select.select(r, w, x, timeout)
    except select.error, e:
        if e[0] == errno.EINTR:
            return [], [], []
        raise

