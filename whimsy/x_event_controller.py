# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

from whimsy import signals

class x_event_controller(signals.publisher):
    def __init__(self, dpy, **event_attrs):
        signals.publisher.__init__(self, **event_attrs)
        self.dpy = dpy
        self.event_attrs = event_attrs

    def emit_all_pending_events(self):
        for i in xrange(self.dpy.pending_events()):
            self.emit_next_event()

    def emit_next_event(self):
        ev = self.dpy.next_event()
        # signals.publisher already does this...
        for attr, val in self.event_attrs.items():
            setattr(ev, attr, val)
        self.signal('event_begin', ev=ev)
        self.signal('event',       ev=ev)
        self.signal('event_done',  ev=ev)
    
