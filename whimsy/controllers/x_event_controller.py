# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy.util import lenient_select

class x_event_controller(object):
    def __init__(self, hub, dpy, **event_attrs):
        self.hub = hub
        self.dpy = dpy
        self.event_attrs = event_attrs

    def select_and_emit_all(self, signal):
        lenient_select([self.dpy], [], [], 1.0/100)
        self.emit_all_pending_events()

    def emit_all_pending_events(self):
        for i in xrange(self.dpy.pending_events()):
            self.emit_next_event()

    def emit_next_event(self):
        ev = self.dpy.next_event()
        # signals.publisher already does this...
        for attr, val in self.event_attrs.items():
            setattr(ev, attr, val)
        self.hub.signal('event_begin', ev=ev, win=ev.window)
        self.hub.signal('event',       ev=ev, win=ev.window)
        self.hub.signal('event_done',  ev=ev, win=ev.window)
    
