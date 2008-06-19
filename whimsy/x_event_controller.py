# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

class x_event_controller(object):
    def __init__(self, dpy, hub, **event_attrs):
        self.dpy = dpy
        self.hub = hub
        self.event_attrs = event_attrs

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
    
