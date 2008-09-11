# Written by Nick Welch in the years 2005-2008.  Author disclaims copyright.

class tick_controller(object):
    alive = False
    def __init__(self, hub):
        self.hub = hub

    def tick_forever(self):
        self.alive = True
        while self.alive:
            self.hub.emit('tick')

    def stop(self):
        self.alive = False
    
