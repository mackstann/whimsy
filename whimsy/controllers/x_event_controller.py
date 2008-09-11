# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.util import lenient_select

import re

capital_letter_re = re.compile(r'\B([A-Z])')

class x_event_controller(object):
    def __init__(self, hub, dpy):
        self.hub = hub
        self.dpy = dpy

    def select_and_emit_all(self, **kw):
        lenient_select([self.dpy], [], [], 1.0/100)
        self.emit_all_pending_events()

    def emit_all_pending_events(self):
        for i in xrange(self.dpy.pending_events()):
            self.emit_next_event()

    def emit_next_event(self):
        ev = self.dpy.next_event()
        # the specific event name, like button_press (converted from ButtonPress)
        lowered = capital_letter_re.sub('_\\1', ev.__class__.__name__).lower()
        self.hub.emit('event_begin', ev=ev, win=ev.window)
        self.hub.emit(lowered,       ev=ev, win=ev.window)
        self.hub.emit('event',       ev=ev, win=ev.window)
        self.hub.emit('event_done',  ev=ev, win=ev.window)
    
