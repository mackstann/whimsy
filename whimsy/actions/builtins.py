# Whimsy is written by Nick Welch <mack@incise.org>, 2005-2007.
#
# This software is in the public domain
# and is provided AS IS, with NO WARRANTY.

import os

from whimsy.log import *

from whimsy import transformers, props, window_manager, util
import whimsy.window_manager.util

#####################################################################
############################## public ###############################
#####################################################################

class delete_client:
    def __call__(self, signal):
        c = signal.wm.window_to_client(signal.ev.window)
        c.delete()
        signal.wm.clients.remove(c)

# implement _WHIMSY_CLIENT_LIST_FOCUS -> lists managed windows that have been
# focused, most recent first

class focus_tracker:
    def record_focus_event(self, signal):
        wins = props.get_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS')
        debug('record')
        if signal.ev.window.id in wins:
            wins.remove(signal.ev.window.id)
        wins.insert(0, signal.ev.window.id)
        props.change_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS', wins)

    def focus_last_focused(self, signal):
        wins = props.get_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS')
        debug('focus old')
        while wins:
            c = signal.wm.window_id_to_client(wins[0])
            if c:
                c.focus()
                break
            wins.pop(0)
        props.change_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS', wins)

class start_move:
    def __call__(self, signal):
        signal.wm.register('event_begin',
            transformers.move_transformer(
                signal.wm.window_to_client(signal.ev.window),
                signal.ev
            )
        )

class start_resize:
    def __call__(self, signal):
        signal.wm.register('event_begin',
            transformers.resize_transformer(
                signal.wm.window_to_client(signal.ev.window),
                signal.ev
            )
        )

class client_method:
    def __init__(self, methodname, *a, **kw):
        self.methodname = methodname
        self.a = a
        self.kw = kw

    def __call__(self, signal):
        getattr(
            signal.wm.window_to_client(signal.ev.window),
            self.methodname
        )(*self.a, **self.kw)

class execute:
    def __init__(self, cmd):
        self.cmd = cmd
    def __call__(self, signal):
        if not os.fork():
            os.setsid()
            if not os.fork():
                os.execvp('/bin/sh', ['sh', '-c', self.cmd])
            os._exit(0)

class viewport_absolute_move:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __call__(self, signal):
        current_x, current_y = props.get_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_VIEWPORT'
        )

        if current_x == self.x and current_y == self.y:
            return

        window_manager.util.move_viewport_to(
            signal.wm,
            current_x, current_y,
            self.x, self.y,
        )

class viewport_relative_move:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __call__(self, signal):
        root = signal.wm.root.get_geometry()

        total_width, total_height = props.get_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_GEOMETRY'
        )
        current_x, current_y = props.get_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_VIEWPORT'
        )

        move_to_x = current_x + self.x
        move_to_y = current_y + self.y

        furthest_x = total_width - root.width
        furthest_y = total_height - root.height

        if not 0 <= move_to_x <= furthest_x or not 0 <= move_to_y <= furthest_y:
            return

        window_manager.util.move_viewport_to(
            signal.wm,
            current_x, current_y,
            self.x, self.y,
        )

