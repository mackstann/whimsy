# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import Xutil
import sys, math

class size_hints(object):
    def __init__(self, **kw):
        if 'hints' in kw and 'win' not in kw:
            self.hints = kw["hints"]
        elif 'win' in kw:
            self.hints = kw["win"].get_wm_normal_hints()
        else:
            raise ValueError(
                "pass either a 'win' or 'hints' argument, but not both")

    def __get(self, attr, flag, lowerbound, default):
        if self.hints and self.hints.flags & flag:
            return max(getattr(self.hints, attr), lowerbound)
        return default

    def __get_aspect(self, attr):
        if self.hints and self.hints.flags & Xutil.PAspect:
            aspect = getattr(self.hints, attr)
            if aspect.num and aspect.denum:
                return max(float(aspect.num) / aspect.denum, 0.0)
        return 0.0

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

    # icccm:
    #
    # "The base_width and base_height elements in conjunction with width_inc
    # and height_inc define an arithmetic progression of preferred window
    # widths and heights for nonnegative integers i and j:
    #
    #     width = base_width + (i x width_inc)
    #     height = base_height + (j x height_inc) 
    #
    # Window managers are encouraged to use i and j instead of width and height
    # in reporting window sizes to users. If a base size is not provided, the
    # minimum size is to be used in its place and vice versa."
    #
    # (last sentence ONLY applies to dealing with incremental window sizes)

    def get_human_width(self, width):
        base_width = self.base_width if self.hints.flags & Xutil.PBaseSize \
            else self.min_width
        return (width - base_width) / self.width_inc

    def get_human_height(self, height):
        base_width = self.base_height if self.hints.flags & Xutil.PBaseSize \
            else self.min_height
        return (height - base_height) / self.height_inc

    def get_gravity(self, default):
        if self.hints and self.hints.flags & Xutil.PWinGravity:
            return self.hints.win_gravity
        return default

    def fix_increments(self, width, height):
        if self.hints and self.hints.flags & Xutil.PBaseSize:
            basew, baseh = self.base_width, self.base_height
        else:
            basew, baseh = self.min_width, self.min_height
        return width - (width - basew) % self.width_inc, \
            height - (height - baseh) % self.height_inc

    def fix_max(self, width, height):
        return min(width, self.max_width), min(height, self.max_height)

    def fix_min(self, width, height):
        if self.hints and self.hints.flags & Xutil.PMinSize:
            minw, minh = self.min_width, self.min_height
        else:
            minw, minh = self.base_width, self.base_height
        return max(width, minw), max(height, minh)

    def fix_aspect(self, width, height):
        # icccm: "If a base size is provided along with the aspect ratio
        # fields, the base size should be subtracted from the window size prior
        # to checking that the aspect ratio falls in range. If a base size is
        # not provided, nothing should be subtracted from the window size. (The
        # minimum size is not to be used in place of the base size for this
        # purpose.)"

        w = max(width, 1)
        h = max(height, 1)
        base_width = self.base_width
        base_height = self.base_height

        if w == base_width and h == base_height:
            return w, h

        aspect_relevant_width = w - self.base_width
        aspect_relevant_height = h - self.base_height

        try:
            aspect = float(aspect_relevant_width / aspect_relevant_height)
        except ZeroDivisionError:
            aspect = 0.0

        minaspect = self.min_aspect
        maxaspect = self.max_aspect

        if maxaspect and aspect > maxaspect:
            return self.change_to_aspect(maxaspect, w, h)
        elif minaspect and aspect < minaspect:
            return self.change_to_aspect(minaspect, w, h)

        return w, h

    def change_to_aspect(self, aspect, width, height):
        """
        aspect is a float, e.g. 1.3... for 4:3 (4/3), 1.7... for 16:9 (16/9)

        take a non-aspect-ratio-conforming width and height, and return a new
        width and height that conforms (as close as possible) to the respective
        aspect ratio while maintaining (as close as possible) the same amount
        of area

        width = height x aspect, so:
        area = height x height x aspect

        new_height x new_height x aspect = orig_width x orig_height
        new_height**2 x aspect = orig_width x orig_height
        new_height**2 = (orig_width x orig_height) / aspect
        new_height = sqrt((orig_width x orig_height) / aspect)

        so: 4096 x 75
        becomes: 480 x (4/3.0) x 480
        which is: 640 x 480
        4096 x 75 = 640 x 480 = 307200
        """
        new_height = int(round(math.sqrt((width * height) / aspect)))
        new_width = int(round(new_height * aspect))
        return new_width, new_height

