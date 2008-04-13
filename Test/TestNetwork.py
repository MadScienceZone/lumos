from Network import Network

class TestNetwork (Network):
    """
	This is a network type for debugging purposes.  Instead of talking
	to an external device, it simply prints its commands to stdout.
    """
    
    def __init__(self, id, **kwargs):
        self.id = id
        self.units = {}
		self.closed = False
		print "DEBUG: TestNetwork: cons(%s, %s)" % (
			id, ', '.join(["%s=%s" % (k, v) for k, v in kwargs.items()])
		)

    def add_unit(self, id, unit):
        "Add a new controller unit to the network."
		if self.closed: raise ValueError, "Device already closed!"
        self.units[id] = unit
		print "DEBUG: TestNetwork: add_unit(%s, %s)" % (
			id, unit
		)

    def send(self, cmd):
        "Send a command string to the hardware device."
		if self.closed: raise ValueError, "Device already closed!"
		print "DEBUG: TestNetwork: send(%s)" % cmd ; # XXX Needs binary protection

    def close(self):
        """Close the network device; no further operations are
        possible for it."""
		if self.closed: raise ValueError, "Device already closed!"
		print "DEBUG: TestNetwork: close()"
		self.closed = True
