# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

class x_event_manager:
    def __init__(self, dpy, **event_attrs):
        self.dpy = dpy
        self.events = [] # [oldest_event, ..., newest_event]
        self.event_attrs = event_attrs

    def process_one_event(self):
        ev = self.next_event()
        self.signal('event_begin', ev=ev)
        self.signal('event',       ev=ev)
        self.signal('event_done',  ev=ev)
    
    def next_event(self):
        ev = self.events.pop(0)
        for attr, val in self.event_attrs.items():
            setattr(ev, attr, val)
        return ev

    def pull_all_pending_events(self):
        self.events.extend([
            self.dpy.next_event() for i in range(self.dpy.pending_events())
        ])

    def handle_all_pending_events(self):
        while self.events:
            self.process_one_event()

