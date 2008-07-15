# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from Xlib import X
import select, errno

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

def lenient_select(r, w, x, timeout):
    # sigchld for example will interrupt select() and cause an unhandled
    # socket.error exception.
    try:
        return select.select(r, w, x, timeout)
    except select.error, e:
        if e[0] == errno.EINTR:
            return [], [], []
        raise

