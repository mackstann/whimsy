# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

import os, subprocess

from whimsy import transformers, props, window_manager, util, client
import whimsy.window_manager.util

#####################################################################
############################## public ###############################
#####################################################################

class delete_client:
    def __call__(self, signal):
        c = signal.wm.window_to_client(signal.ev.window)
        c.delete()
        signal.wm.clients.remove(c)
        signal.wm.signal('after_delete_client', win=signal.ev.window)

# _WHIMSY_CLIENT_LIST_FOCUS: lists managed windows that have been
# focused, most recent first

def update_client_list_focus(signal):
    wins = props.get_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS')
    if signal.ev.window.id in wins:
        wins.remove(signal.ev.window.id)
    wins.insert(0, signal.ev.window.id)
    props.change_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS', wins)

def focus_last_focused(signal):
    wins = props.get_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS')
    while wins:
        c = signal.wm.window_id_to_client(wins[0])
        if c:
            c.focus()
            break
        wins.pop(0)
    props.change_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_CLIENT_LIST_FOCUS', wins)

pixel_distance = 15
timeout_ms = 400

def update_last_button_press(signal):
    try:
        class prev:
            window_id, detail, state, time, root_x, root_y = props.get_prop(
                signal.wm.dpy, signal.wm.root, '_WHIMSY_LAST_BUTTON_PRESS'
            )
    except ValueError:
        is_repeat = False
    else:
        is_repeat = (
            signal.ev.window.id == prev.window_id and
            signal.ev.detail == prev.detail and
            signal.ev.state == prev.state and
            (signal.ev.time - prev.time) <= timeout_ms and
            abs(signal.ev.root_x - prev.root_x) <= pixel_distance and
            abs(signal.ev.root_y - prev.root_y) <= pixel_distance
        )

    count = 1
    if is_repeat:
        count += props.get_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_MULTICLICK_COUNT')

    props.change_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_MULTICLICK_COUNT', count)
    props.change_prop(signal.wm.dpy, signal.wm.root, '_WHIMSY_LAST_BUTTON_PRESS', [
        signal.ev.window.id,
        signal.ev.detail,
        signal.ev.state,
        signal.ev.time,
        signal.ev.root_x,
        signal.ev.root_y
    ])

class start_move:
    def __call__(self, signal):
        signal.wm.register('event_begin',
            transformers.move_transformer(
                signal.wm.dpy,
                signal.wm.window_to_client(signal.ev.window),
                signal.ev
            )
        )

class start_resize:
    def __call__(self, signal):
        signal.wm.register('event_begin',
            transformers.resize_transformer(
                signal.wm.dpy,
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
        if hasattr(signal, 'client'):
            c = signal.client
        else:
            c = signal.wm.window_to_client(signal.ev.window)
        getattr(c, self.methodname)(*self.a, **self.kw)

class execute:
    def __init__(self, cmd):
        self.cmd = cmd
    def __call__(self, signal):
        if not os.fork():
            os.setsid()
            subprocess.Popen(['/bin/sh', '-c', self.cmd], close_fds=True)
            os._exit(0)

class viewport_absolute_move:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __call__(self, signal):
        current_x, current_y = props.get_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_VIEWPORT'
        )
        window_manager.util.move_viewport_to(
            signal.wm,
            current_x, current_y,
            self.x, self.y,
        )

class viewport_relative_move:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __call__(self, signal):
        if not hasattr(self, 'root_geom'):
            self.root_geom = signal.wm.root.get_geometry()

        total_width, total_height = props.get_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_GEOMETRY'
        )
        current_x, current_y = props.get_prop(
            signal.wm.dpy, signal.wm.root, '_NET_DESKTOP_VIEWPORT'
        )

        move_to_x = current_x + self.x
        move_to_y = current_y + self.y

        limit_x = total_width - self.root_geom.width
        limit_y = total_height - self.root_geom.height

        if 0 <= move_to_x <= limit_x and 0 <= move_to_y <= limit_y:
            viewport_absolute_move(move_to_x, move_to_y)(signal)

def discover_existing_windows(signal):
    for win in signal.wm.root.query_tree().children:
        signal.wm.signal('existing_window_discovered', win=win)

def manage_window(signal):
    win = util.signal_window(signal)
    c = client.managed_client(signal.wm, win)
    signal.wm.clients.append(c)
    signal.wm.signal('after_manage_window', win=win)

